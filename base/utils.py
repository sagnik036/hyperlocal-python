import base64
import math
import os
import io
import traceback
import urllib
import mimetypes
from urllib.request import urlopen
import random
import string
import magic
import secrets
import six
import logging
import pytz

from collections import OrderedDict
import json
import requests
from io import BytesIO
from tempfile import SpooledTemporaryFile

import boto3
import phonenumbers
from django.conf import settings
from django.contrib.auth.password_validation import \
    get_default_password_validators
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import TemporaryUploadedFile
from django.core.paginator import InvalidPage
from django.db.models import IntegerField, Subquery
from django.http import QueryDict
from django.utils import timezone
from PIL import Image
from rest_framework import serializers, status
from rest_framework.pagination import (LimitOffsetPagination,
                                       PageNumberPagination)
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from storages.backends.s3boto3 import S3Boto3Storage


logger = logging.getLogger('__name__')


class CustomS3Boto3Storage(S3Boto3Storage):

    def _save_content(self, obj, content, parameters):
        """
        We create a clone of the content file as when this is passed to boto3 it wrongly closes
        the file upon upload where as the storage backend expects it to still be open
        """
        # Seek our content back to the start
        content.seek(0, os.SEEK_SET)

        # Create a temporary file that will write to disk after a specified size
        content_autoclose = SpooledTemporaryFile()

        # Write our original content into our copy that will be closed by boto3
        content_autoclose.write(content.read())

        # Upload the object which will auto close the content_autoclose instance
        super(
            CustomS3Boto3Storage,
            self)._save_content(
            obj,
            content_autoclose,
            parameters)

        # Cleanup if this is fixed upstream our duplicate should always close
        if not content_autoclose.closed:
            content_autoclose.close()


class StaticFileStorage(CustomS3Boto3Storage):
    default_acl = 'public-read'
    querystring_auth = False


class CustomException(Exception):
    pass


class CapitalLetterValidator(object):
    HELP_TEXT = 'Password should contain at least one capital letter'

    def validate(self, password, user=None):
        if not any(str(x).isupper() for x in password):
            raise ValidationError(self.HELP_TEXT)

    def get_help_text(self):
        return self.HELP_TEXT


class NumericCharacterValidator(object):
    HELP_TEXT = 'Password should contain at least one number'

    def validate(self, password, user=None):
        if not any(x in string.digits for x in password):
            raise ValidationError(self.HELP_TEXT)

    def get_help_text(self):
        return self.HELP_TEXT


class SpecialCharacterValidator(object):
    HELP_TEXT = 'Password should contain at least one special character'

    def validate(self, password, user=None):
        if not any(x in string.punctuation for x in password):
            raise ValidationError(self.HELP_TEXT)

    def get_help_text(self):
        return self.HELP_TEXT


def custom_password_validator(password, user=None, password_validators=None):
    errors = []
    if ' ' in password:
        errors.append('Password cannot contain blank space')
    if password_validators is None:
        password_validators = get_default_password_validators()
    for validator in password_validators:
        try:
            validator.validate(password, user)
        except ValidationError as error:
            errors.extend(error.messages)

    if errors:
        if user:
            raise serializers.ValidationError(detail={'password': errors})
        else:
            raise serializers.ValidationError(detail=errors)


def validate_image(value):
    if hasattr(value, 'content_type'):
        if value.content_type.split('/')[0] != 'image':
            raise serializers.ValidationError(
                detail='Please upload a valid image file')
    if value.size > settings.MAX_UPLOAD_SIZE:
        raise serializers.ValidationError(
            detail='File size should be less than 10 Megabytes')


def get_image_from_b64(data):
    format, imgstr = data.split(';base64')
    random_name = ''.join(random.choice(string.ascii_letters)
                          for _ in range(9))
    filename = random_name + '.png'
    image = ContentFile(base64.b64decode(imgstr), name=filename)
    return image


def get_file_from_url(url):
    req = urllib.request.Request(url, headers={'User-Agent': "Magic Browser"})
    input_file = io.BytesIO(urlopen(req).read())
    content_type = magic.from_buffer(input_file.getvalue(), mime=True)
    extension = mimetypes.guess_extension(content_type)
    temp_file = TemporaryUploadedFile(name=secrets.token_hex(10) + extension,
                                      content_type=content_type,
                                      size=input_file.__sizeof__(),
                                      charset=None)
    temp_file.file.write(input_file.getvalue())
    temp_file.file.seek(0)
    return extension, temp_file


def get_dict_data(data):
    if isinstance(data, dict):
        return data
    else:
        return data.dict()


class CustomLimitOffsetPagination(LimitOffsetPagination):
    max_limit = 100


class CustomPagination(PageNumberPagination):
    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('total_pages', math.ceil(self.page.paginator.count / self.page_size)),
            ('data', data)
        ]))

    def paginate_queryset(self, queryset, request, view=None):
        """
        Paginate a queryset if required, either returning a
        page object, or `None` if pagination is not configured for this view.
        """
        page_size = self.get_page_size(request)
        if not page_size:
            return None

        paginator = self.django_paginator_class(queryset, page_size)
        page_number = request.query_params.get(self.page_query_param, 1)
        if page_number in self.last_page_strings:
            page_number = paginator.num_pages

        try:
            self.page = paginator.page(page_number)
        except InvalidPage as exc:
            msg = self.invalid_page_message.format(
                page_number=page_number, message=six.text_type(exc)
            )
            raise InvalidPage(msg)

        if paginator.num_pages > 1 and self.template is not None:
            # The browsable API should display pagination controls.
            self.display_page_controls = True

        self.request = request
        return list(self.page)


def paginated_success_response(data, message=None):
    return Response({'status': {'code': status.HTTP_200_OK,
                                'message': message},
                     **data})


def success_response(data=None, message=None, request=None, extra_data={}):
    result = {'status': {'code': status.HTTP_200_OK,
                         'message': message},
              'data': data
              }
    result.update(extra_data)
    return Response(result)


def error_response(data=None, message=None, request=None, code=status.HTTP_403_FORBIDDEN):
    return Response({'status': {'code': code,
                                'message': message},
                     'data': data
                     })


def phonenumber_validator(value):
    try:
        z = phonenumbers.parse(value, None)
        if not phonenumbers.is_valid_number(z):
            raise ValidationError('Please enter a valid phone number')
    except Exception as e:
        if settings.ENV == 'development':
            raise ValidationError(str(e))
        else:
            raise ValidationError(
                'Please enter a valid phone number with international code')
    return phonenumbers.format_number(z, phonenumbers.PhoneNumberFormat.E164)


def create_otp(length):
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])


# def disposable_mail_validator(value):
#     value = value.lower()
#     if not MailChecker.MailChecker.is_valid(value) and not settings.DEBUG:
#         raise ValidationError('Please enter a valid email')
#     return value


def get_jwt_auth_token(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


def random_file_name(extension, length):
    random_name = ''.join(random.choice(string.ascii_letters)
                          for _ in range(length))
    return random_name + timezone.localdate().strftime('%Y%m%d') + extension


class SQCount(Subquery):
    template = "(SELECT count(*) FROM (%(subquery)s) _count)"
    output_field = IntegerField()


def get_sms_client():
    sms_client = boto3.client("sns", region_name=settings.SNS_REGION)
    sms_client.set_sms_attributes(
        attributes={"DefaultSMSType": "Transactional"}
    )
    return sms_client


def make_mutable(data):
    return setattr(data, '_mutable', True) if type(data) == QueryDict else None


def get_boolean(x):
    if type(x) == bool:
        return x
    if x:
        if x.lower() == 'true' or x == 1 or x == '1' or x == 't':
            return True
        else:
            return False
    else:
        return False


def get_thumbnail_url(url):
    s3 = boto3.client('s3')
    thumbnail_url = s3.generate_presigned_url(
        'get_object',
        Params={
            'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
            'Key': 'thumbnails/' + '.'.join(url.split('.')[:-1] + ['png']),
            'ResponseExpires': timezone.now() + timezone.timedelta(hours=23)
        }
    )
    return thumbnail_url

def get_geo_data(x,y):
    url = f'https://nominatim.openstreetmap.org/reverse?format=json&lat={y}&lon={x}'
    response = requests.get(url)
    data = response.json()
    return data