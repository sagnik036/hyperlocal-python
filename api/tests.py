import csv
import logging
import os
import secrets
from io import StringIO
import io
import requests
import json
import boto3
import firebase_admin
import requests
from celery.signals import task_failure
from django.conf import settings
from django.db.models import Prefetch, F
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from firebase_admin import credentials, messaging
from rest_framework_simplejwt.backends import TokenBackend

from base.choices import NotificationType
from api.models import AdminNotification, CustomUser, UserNotification
from hyperlocal.celery import common_app as app
from base.utils import get_sms_client
from django.core.mail import send_mail, EmailMessage, EmailMultiAlternatives
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from base.choices import DeviceType
from django.db import transaction





# cred = credentials.Certificate(os.path.join(settings.BASE_DIR, 'google-service-account.json'))
# firebase_admin.initialize_app(cred)

logger = logging.getLogger('__name__')


@app.task()
def send_fcm_to_token(token, data, notification,device_type):
    try:
        message = messaging.Message(
            data=data,
            notification=messaging.Notification(**notification),
            token=token,
        )
        if device_type == DeviceType.ios.value[0]:
            message.apns = messaging.APNSConfig(
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(
                        sound='default',
                        content_available=True,
                        mutable_content=True)))


        elif device_type == DeviceType.android.value[0]:

            message.android = messaging.AndroidConfig(
                data=data,
                notification=messaging.AndroidNotification(**notification)
            )

        elif device_type == DeviceType.web.value[0]:
            message.webpush = messaging.WebpushConfig(
                data=data,
                notification=messaging.WebpushNotification(**notification)
            )

        response = messaging.send(message)
        logger.info({
            'ref': 'Push message sending response',
            'device_token': token,
            'notification': notification,
            'payload': data,
            'response': response
            })

    except Exception as e:
        logger.error({
            'ref': 'Error while sending Push message',
            'device_token': token,
            'notification': notification,
            'payload': data,
            'error': str(e)
            })


@app.task()
def send_mail_task(subject, html_message, recipient_list):
    from_email = f'{settings.EMAIL_FROM_NAME} <{settings.DEFAULT_FROM_EMAIL}>'
    send_mail(subject=subject, message=strip_tags(html_message), html_message=html_message, from_email=from_email, recipient_list=recipient_list)
    return {'Recipients': recipient_list, 'Subject': subject}


@app.task()
def send_notification_to_users(user_ids, notification_type,
                               title, body, extra_data={}, admin_notification_id=None):
    if user_ids is None:  # means notification was sent to all users
        users = CustomUser.objects.all().prefetch_related('devicetoken_set')
    else:
        users = CustomUser.objects.filter(
            id__in=user_ids).prefetch_related('devicetoken_set')
    if admin_notification_id:
        admin_notification = AdminNotification.objects.get(id=admin_notification_id)
    else:
        admin_notification = None
    for user in users:
        user_notification = UserNotification.objects.create(
            notification_type=notification_type,
            user=user,
            title=title,
            body=body,
            admin_notification=admin_notification,
            data_id=extra_data.get('data_id'))
        if user.notification_setting:
            data = {
                'notification_type': notification_type
            }
            data.update(extra_data)
            notification = {
                'title': title,
                'body': body
            }
            for device_token in user.devicetoken_set.all():
                send_fcm_to_token(device_token.token, data, notification, device_token.device_type)

    users.update(unread_notification_count=F('unread_notification_count') + 1)
    return f'Sent {notification_type} notifications to users'


@app.task
def send_transactional_sms(mobile_number, message):
    if settings.ENV != 'development':
        sms_client = boto3.client("sns")
        sms_client.set_sms_attributes(
            attributes={"DefaultSMSType": "Transactional"}
        )
        sms_res = sms_client.publish(
            PhoneNumber=mobile_number,
            Message=message,
        )

        logger.info({
            'ref': f'response on sending sms to {mobile_number}',
            'res_data': str(sms_res),
        })
        return f'SMS sent to {mobile_number}'






@app.task()
def send_test_csv_report(test_result, recipient_list):
    string = io.StringIO()
    header = ['S.No', 'Test Name', 'Test Result', 'Test Description', 'Test Message']
    csv_writer = csv.writer(string, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    csv_writer.writerow(header)

    for result_index, result in enumerate(test_result):
        csv_writer.writerow([
            result_index + 1, result['test_name'], result['result'], result['test_description'], result['test_message']
        ])

    email = EmailMultiAlternatives(
        subject=str(timezone.now().strftime("%d-%m-%Y"))+' ' + 'Obstacle Fit' + " CSV report",
        from_email=f'{settings.EMAIL_FROM_NAME} <{settings.DEFAULT_FROM_EMAIL}>',
        to=recipient_list
    )
    email.attach(filename="test_csv_report.csv", content=string.getvalue())
    email.send()
    string.close()
    return f'Mail sent to {recipient_list}'





@task_failure.connect()
def celery_task_failure_email(**kwargs):
    subject = "Celery Error: Task {sender.name} ({task_id}): {exception} | Project: {project_name}".format(
        **kwargs, project_name=settings.EMAIL_FROM_NAME)
    message = """Task {sender.name} with id {task_id} raised exception:
        {exception!r}
        Task was called with args: {args} kwargs: {kwargs}.
        The contents of the full traceback was:
        {einfo}
    """.format(
        **kwargs
    )

    admin_emails = list(map(lambda x: x[1], settings.ADMINS))
    if admin_emails:
        send_mail_task(subject, message, admin_emails)


