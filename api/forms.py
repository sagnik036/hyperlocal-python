from django import forms

from api.models import (AdminNotification, CustomUser, PaymentTerm,
                        PrivacyPolicy, TermAndCondition,ProprietorShop)
from api.task import send_notification_to_users
from base.choices import NotificationType
from base.utils import get_boolean
from django.db import transaction
from strings import *


# class AdminNotificationForm(forms.ModelForm):
#     recipients = forms.ModelMultipleChoiceField(
#         queryset=CustomUser.objects.only('id', 'first_name', 'last_name', 'email', 'mobile_number'),
#         required=False)
#
#     class Meta:
#         model = AdminNotification
#         fields = '__all__'
#
#     def get_initial_for_field(self, field, field_name):
#         field_initials = super().get_initial_for_field(field, field_name)
#         if field_name == 'recipients':
#             field_initials = CustomUser.objects.only('id', 'first_name', 'last_name', 'email', 'mobile_number'
#                                                      ).filter(usernotification__admin_notification_id=self.instance.id)
#         return field_initials
#
#     def save(self, commit=True):
#         super().save(commit=commit)
#
#         send_notification_to_users.apply_async(
#             kwargs={'user_ids': None if self.instance.sent_to_all else [str(x.id) for x in self.cleaned_data['recipients']],
#                     'notification_type': NotificationType.get_value(NotificationType.admin.name),
#                     'title': self.instance.title,
#                     'body': self.instance.description,
#                     'admin_notification_id': str(self.instance.id)
#                     })
#         return self.instance


class TermForm(forms.ModelForm):
    notify_users = forms.BooleanField(required=False)

    class Meta:
        model = TermAndCondition
        fields = ('text', 'document')

    def save(self, commit=True):
        if self.cleaned_data['notify_users'] is True:
            transaction.on_commit(lambda: send_notification_to_users.apply_async(
                kwargs={
                    'user_ids': None,
                    'notification_type': NotificationType.tnc_updated.value[0],
                    'title': TNC_UPDATED_TITLE,
                    'body': TNC_UPDATED_DESCRIPTION
                }
            ))
        return super().save(commit=commit)


class PaymentTermForm(forms.ModelForm):
    notify_users = forms.BooleanField(required=False)

    class Meta:
        model = PaymentTerm
        fields = ('text', 'document')

    def save(self, commit=True):
        if self.cleaned_data['notify_users'] is True:
            transaction.on_commit(lambda: send_notification_to_users.apply_async(
                kwargs={
                    'user_ids': None,
                    'notification_type': NotificationType.payment_terms_updated.value[0],
                    'title': PAYMENT_TERM_UPDATED_TITLE,
                    'body': PAYMENT_TERM_UPDATED_DESCRIPTION
                }
            ))
        return super().save(commit=commit)


class PrivacyPolicyForm(forms.ModelForm):
    notify_users = forms.BooleanField(required=False)

    class Meta:
        model = PrivacyPolicy
        fields = ('text', 'document')

    def save(self, commit=True):
        if self.cleaned_data['notify_users'] is True:
            transaction.on_commit(lambda: send_notification_to_users.apply_async(
                kwargs={
                    'user_ids': None,
                    'notification_type': NotificationType.get_value(
                        NotificationType.privacy_policy_updated.name
                    ),
                    'title': PRIVACY_POLICY_UPDATED_TITLE,
                    'body': PRIVACY_POLICY_UPDATED_DESCRIPTION
                }
            ))
        return super().save(commit=commit)


class AdminNotificationForm(forms.ModelForm):
    class Meta:
        model = AdminNotification
        fields = ('title', 'description', 'sent_to_all', 'recipients')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['recipients'].queryset = CustomUser.objects.none()

        if 'recipients' in self.data:
            self.fields['recipients'].queryset = CustomUser.objects.filter(
                is_superuser=False, is_staff=False, is_active=True)
        elif self.instance and self.instance.recipients:
            if get_boolean(self.instance.sent_to_all):
                self.fields['recipients'].queryset = CustomUser.objects.none()
            else:
                qs = AdminNotification.recipients.through.objects.filter(
                    adminnotification_id=self.instance.id).values_list('customuser_id', flat=True)
                self.fields['recipients'].queryset = CustomUser.objects.filter(id__in=qs)

# class ProprietorShopAdminForm(forms.ModelForm):
#     def clean(self):
#         cleaned_data = super().clean()
#         user = cleaned_data.get("user")
#         if self.instance.id:
#             print(self.instance.id)
#             if ProprietorShop.objects.filter(
#                     user_id=user.id,
#                     is_active=True,
#                     is_job_live = True
#                 ).exists():
#                 self.add_error('is_job_live',CANNOTPERFORM)
#         else:
#             print("s")
#             if ProprietorShop.objects.filter(
#                     user_id=user.id,
#                     is_active=True,
#                 ).exists():
#                 self.add_error('user',SHOPALREADYEXIST)
            
    