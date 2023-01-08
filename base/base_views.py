from rest_framework import serializers, status
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin, UpdateModelMixin, DestroyModelMixin, CreateModelMixin, \
    RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_tracking_logger.mixins import LoggingMixin

from strings import *


class CustomGenericView(LoggingMixin, GenericAPIView):
    def handle_exception(self, exc):
        if isinstance(exc, KeyError):
            exc = serializers.ValidationError(
                detail={exc.args[0]: ['This field is required']})
        return super().handle_exception(exc)


class CustomAPIView(LoggingMixin, APIView):
    def handle_exception(self, exc):
        if isinstance(exc, KeyError):
            exc = serializers.ValidationError(
                detail={exc.args[0]: ['This field is required']})
        return super().handle_exception(exc)


class CustomListModelMixin(ListModelMixin):
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        result = {'status': {'code': status.HTTP_200_OK,
                             'message': None}
                  }
        if 'next' in response.data:  # this tells it is paginated
            result.update(response.data)
        else:
            result['data'] = response.data
        return Response(result)


class CustomCreateModelMixin(CreateModelMixin):
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response({'status': {'code': status.HTTP_200_OK,
                                    'message': kwargs.get('message', CREATE_SUCCESS)},
                         'data': response.data
                         })


class CustomRetrieveModelMixin(RetrieveModelMixin):
    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return Response({'status': {'code': status.HTTP_200_OK,
                                    'message': None},
                         'data': response.data
                         })


class CustomUpdateModelMixin(UpdateModelMixin):
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return Response({'status': {'code': status.HTTP_200_OK,
                                    'message': kwargs.get('message', UPDATE_SUCCESS)},
                         'data': response.data
                         })


class CustomDestroyModelMixin(DestroyModelMixin):
    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({'status': {'code': status.HTTP_200_OK,
                                    'message': DELETE_SUCCESS}
                         })
