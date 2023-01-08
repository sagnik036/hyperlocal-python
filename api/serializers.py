import json

from django.contrib.auth.hashers import make_password
from django.http import QueryDict
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from api.models import AdminContact, CustomUser, DeviceToken, UserNotification,FrequentlyAskedQuestion
from base.utils import get_image_from_b64, phonenumber_validator, custom_password_validator
from strings import *



class CustomPasswordField(serializers.CharField):
    def __init__(self, **kwargs):
        self.required = False
        self.validators.append(custom_password_validator)
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        data = make_password(data)
        return super().to_internal_value(data)


class CustomEmailField(serializers.EmailField):
    def to_internal_value(self, data):
        data = data.lower()
        return super().to_internal_value(data)


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str):
            # if (len(data) * 6) > (1024 * 1024):
            #     raise CustomException('Image size cannot be more than 1MB')
            data = get_image_from_b64(data)
        return super().to_internal_value(data)


class CustomListField(serializers.ListField):
    def to_internal_value(self, data):
        if isinstance(self.context["request"].data, QueryDict):
            data = data[0]
        if isinstance(data, str):
            data = json.loads(data)
        return super().to_internal_value(data)


class TextSerializer(serializers.Serializer):
    text = serializers.CharField()
    modified_on = serializers.DateTimeField(read_only=True)
    document = serializers.FileField(required=False)

    def create(self, validated_data):
        instance = self.context["model"](**validated_data)
        instance.save()
        return instance


class AdminContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminContact
        fields = ('email', 'phone_number')


class DeviceTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceToken
        fields = ('device_type', 'token')

    def create(self, validated_data):
        existing_token = DeviceToken.objects.filter(
            device_type=validated_data['device_type'], user_id=validated_data['user'].id).first()
        if existing_token:
            return self.update(existing_token, validated_data)
        return super().create(validated_data)


class UserNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserNotification
        fields = (
            'id',
            'created_at',
            'notification_type',
            'title',
            'body',
            'is_read',
            'data_id'
        )
        read_only_fields = ('notification_type', 'title', 'body', 'data_id')


class CustomUserSerializer(serializers.ModelSerializer):
    notification_setting = serializers.BooleanField(default=True)
    password = serializers.CharField(max_length=100, required=False)
    email = CustomEmailField(
        max_length=254,
        validators=[UniqueValidator(
            queryset=CustomUser.objects.all(),
            message=EMAIL_EXISTS,
            lookup='iexact'
            )]
        )
    password = CustomPasswordField()

    class Meta:
        model = CustomUser
        fields = (
            
            'id',
            'password',
            'date_joined',
            'first_name',
            'last_name',
            'email',
            'mobile_number',
            'user_type',
            'is_shop',
            'live_jobs_count',
            'total_jobs_posted',
            'is_email_verified',
            'is_mobile_verified',
            'is_superuser',
            'last_login',
             
            
        )
        read_only_fields = (
            'date_joined',
            'last_login',
            'is_superuser',
        )

    def validate_mobile_number(self, value):
        if value:
            value = phonenumber_validator(value)
        return value

    def update(self, instance, validated_data):
        if validated_data.get('mobile_number'):
            if validated_data.get('mobile_number') != instance.mobile_number:
                validated_data['is_mobile_verified'] = False
        if validated_data.get('email'):
            if validated_data.get('email') != instance.email:
                validated_data['is_email_verified'] = False
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.pop('password')
        return data


class UserPasswordSerializer(serializers.ModelSerializer):
    password = CustomPasswordField(required=True)

    class Meta:
        model = CustomUser
        fields = ("password",)

class FrequentlyAskedQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FrequentlyAskedQuestion
        fields = ("id", "created_at", "modified_at", "question", "answer")
