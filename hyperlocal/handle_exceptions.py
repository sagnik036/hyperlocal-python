import logging
import traceback

from django.apps import apps
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.paginator import InvalidPage
from django.db import IntegrityError
from django.db.models import ProtectedError
from django.http import Http404
from rest_framework import serializers, status
from rest_framework.exceptions import (AuthenticationFailed, MethodNotAllowed,
                                       NotAuthenticated, PermissionDenied,
                                       Throttled)
from rest_framework.response import Response
from rest_framework.views import exception_handler
from rest_framework_simplejwt.exceptions import TokenBackendError

from base.utils import CustomException
from strings import *



logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    logger.exception({
        'ref': 'Exception caught in common exception handler',
        'exception': str(exc),
        'traceback': traceback.format_exc()
    })

    code = status.HTTP_403_FORBIDDEN
    detail = None
    message = 'Server Error'

    if isinstance(exc, PermissionDenied):
        message = exc.__str__()

    if isinstance(exc, MethodNotAllowed):
        message = exc.__str__()

    for i in apps.get_models():
        if isinstance(exc, i.DoesNotExist):
            # model_name = re_camel_case.sub(r' \1', i.__name__).strip()
            message = "Matching result not found"
            code = status.HTTP_404_NOT_FOUND

    if isinstance(exc, Http404):
        message = "Matching result not found"
        code = status.HTTP_404_NOT_FOUND

    if isinstance(exc, IntegrityError):
        message = 'Invalid request'

    if isinstance(exc, ProtectedError):
        message = 'Cannot delete'

    if isinstance(exc, InvalidPage):
        code = status.HTTP_417_EXPECTATION_FAILED
        message = "Invalid Page"

    if isinstance(exc, serializers.ValidationError):
        message = 'Please correct the errors below.'
        detail = exc.detail

    if isinstance(exc, ValidationError):
        if len(exc.messages):
            message = exc.messages[0]

    if isinstance(exc, CustomException):
        message = exc.__str__()

    if isinstance(exc, PermissionError):
        message = 'Forbidden'

    if isinstance(exc, TokenBackendError):
        message = 'Invalid link'

    

    if isinstance(exc, (AuthenticationFailed, NotAuthenticated)):
        code = status.HTTP_401_UNAUTHORIZED
        message = 'Authentication Failed'

    if isinstance(exc, Throttled):
        message = 'Please try after sometime'

    result = {'status': {'code': code,
                         'message': message,
                         'detail': detail}
              }
    return Response(result)
