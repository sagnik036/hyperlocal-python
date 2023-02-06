import json

from django.contrib.auth.hashers import make_password
from django.http import QueryDict
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.gis.geos import Point
from api.models import (AdminContact, CustomUser, DeviceToken, \
    UserNotification,FrequentlyAskedQuestion,ProprietorShop)
from base.utils import get_image_from_b64, phonenumber_validator, custom_password_validator
from strings import *
from rest_framework_gis.serializers import GeoFeatureModelSerializer


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
    password = serializers.CharField(max_length=100, required=False)
    email = CustomEmailField(
        max_length=254,
        required = False,
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
            'is_adhar_verified',
            'adhar_photo_front',
            'adhar_photo_back',
            'live_jobs_count',
            'total_jobs_posted',
            'is_email_verified',
            'is_mobile_verified',
            'profile_pic',
            'is_superuser',
            'last_login',   
        )

        read_only_fields = (
            'date_joined',
            'is_adhar_verified',
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


""" m2 serializers  --> """

class UserListSerializers(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            "id",
            'date_joined',
            'first_name',
            'last_name',
            'email',
            'mobile_number',
            'total_jobs_posted',
            'profile_pic',
        )


class ShopListSerializers(serializers.ModelSerializer):
    user = UserListSerializers(read_only = True)

    class Meta:
        model = ProprietorShop
        fields = (
            "id",
            "user",
            "shop_photo",
            "shop_name",
            "shop_shortdescribtion",
            "location",
            "shop_address",
        )
        read_only_fields =(
            "id",
            "shop_photo",
            "shop_name",
            "shop_shortdescribtion",
            "location",
            "shop_address",
        )

    
class ShopSerializers(serializers.ModelSerializer):
    # profile_picture = serializers.SerializerMethodField('get_profile_picture')
    user = UserListSerializers(read_only = True)

    class Meta:
        model = ProprietorShop
        fields = (
            "id",
            "user",
            "shop_photo",
            "shop_name",
            "shop_shortdescribtion",
            "shop_describtion",
            "shop_gst",
            "is_active",
            "location",
            "shop_address",
            "shop_country",
            "shop_state",
        )

        read_only_fields =(
            "id",
            "is_active",
            "shop_address",
            "shop_country",
            "shop_state",
        )

    # """ this will add an extra field the list serializers"""
    # def get_profile_picture(self,obj):
    #     return str(obj.user.profile_pic.url)

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        obj = self.Meta.model(**validated_data)
        obj.full_clean()        
        return super().create(validated_data)
