import uuid

from ckeditor.fields import RichTextField
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.exceptions import ValidationError
# from django.db import models
from django.core.validators import FileExtensionValidator
from base.choices import DeviceType, NotificationType,\
      UserType, VehicleType
from base.utils import StaticFileStorage
from django.contrib.gis.geos import Point
from base.base_upload_handlers import handle_tnc_document, handle_privacy_policy_document, handle_images, handle_payment_term_document, handle_legal_doccuments
from strings import *
from django.db import models
from django.contrib.gis.db.models import PointField
from django.contrib.gis.geos import Point
from django.db.models.signals import pre_delete
from django.dispatch import receiver


class BaseModel(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class TermAndCondition(BaseModel):
    text = RichTextField()
    document = models.FileField(
        upload_to=handle_tnc_document,
        storage=StaticFileStorage(),
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
        null=True,
        blank=True,
    )


class PrivacyPolicy(BaseModel):
    text = RichTextField()
    document = models.FileField(
        upload_to=handle_privacy_policy_document,
        storage=StaticFileStorage(),
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
        null=True,
        blank=True,
    )


class PaymentTerm(BaseModel):
    text = RichTextField()
    document = models.FileField(
        upload_to=handle_payment_term_document,
        storage=StaticFileStorage(),
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
        null=True,
        blank=True,
    )


class AdminContact(BaseModel):
    email = models.EmailField()
    phone_number = models.CharField(max_length=50)

    def __str__(self):
        return self.email


class CustomUserManager(UserManager):
    def _create_user(self, mobile_number, password, **extra_fields):
        """
        Create and save a user with the given username, mobile_number, and password.
        """
        user = self.model(mobile_number=mobile_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, mobile_number=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(mobile_number, password, **extra_fields)

    def create_superuser(self, mobile_number, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(mobile_number, password, **extra_fields)


class CustomUser(AbstractUser):
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    username = None
    profile_pic = models.ImageField(
        upload_to='images/', 
        blank=True
    )
    email = models.EmailField(
        error_messages={"unique": "A user with that email already exists"},
        null= True,
        blank= True,
    )
    mobile_number = models.CharField(
        error_messages={"unique": "A user with that mobile already exists"},
        max_length=50,
        unique=True,
    )
    is_email_verified = models.BooleanField(default=False)
    is_mobile_verified = models.BooleanField(default=False)
    user_type = models.CharField(
        max_length=20,
        choices=[x.value for x in UserType],
        blank=True,
        null= True
    )

    #if user has shop
    is_shop = models.BooleanField(
        default=False,
        verbose_name="have shop"
    )
    
    #adharcard photo
    adhar_photo_front = models.ImageField(
        upload_to='images/',
        verbose_name= "Adharcard front"
    )
    adhar_photo_back = models.ImageField(
        upload_to='images/',
        verbose_name="Adharcard Back"
    )


    #if adhar verified or not
    is_adhar_verified = models.BooleanField(
        default=False,
        verbose_name="AdharCard Verified"
    )

    #auto fields -> to be calculated
    live_jobs_count = models.PositiveIntegerField(default=0)
    total_jobs_posted = models.PositiveIntegerField(default=0)


    # notification_setting = models.BooleanField(default=True)
    # unread_notification_count = models.PositiveIntegerField(default=0)

    USERNAME_FIELD = 'mobile_number'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def save(self, *args, **kwargs):

        if self.mobile_number:
            if CustomUser.objects.filter(
                    mobile_number=self.mobile_number).exclude(id=self.id).exists():
                raise ValidationError(MOBILE_EXISTS)
        super().save(*args, **kwargs)

    def validate_unique(self, exclude=None):
        if not self.email.islower():
            self.email = self.email.lower()
        super().validate_unique(exclude=['id'])

    class Meta:
        ordering = ('first_name',)
        verbose_name_plural = 'Users'
        verbose_name = 'User'


class DeviceToken(BaseModel):
    device_type = models.CharField(max_length=10, choices=[
                                   x.value for x in DeviceType])
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    token = models.TextField()

    class Meta:
        ordering = ('-created_at',)


class UserNotification(BaseModel):
    notification_type = models.CharField(
        max_length=20, choices=[x.value for x in NotificationType])
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    body = models.CharField(max_length=500)
    is_read = models.BooleanField(default=False)
    admin_notification = models.ForeignKey(
        'AdminNotification', on_delete=models.SET_NULL, null=True)
    data_id = models.CharField(max_length=250, null=True, blank=True)

    class Meta:
        ordering = ('-created_at',)


class AdminNotification(BaseModel):
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=250)
    # to indicate admin that this notification was sent to all
    sent_to_all = models.BooleanField(default=False)
    recipients = models.ManyToManyField(CustomUser, blank=True,
                                        help_text="<b>Note:It will send the notification to the selected user only.</b>")

    class Meta:
        ordering = ('-created_at',)


class FrequentlyAskedQuestion(BaseModel):
    """
    To be add by app-admin
    """
    question = models.TextField(max_length=2000)
    answer = models.TextField(max_length=2000)

    def __str__(self):
        question = self.question
        if len(question) > 100:
            question = f"{question[0:100]}...."
        return question

    class Meta:
        ordering = ('-created_at',)


"""M2 models"""
class ProprietorShop(BaseModel):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to= {
            'user_type' : UserType.a.value[0],
            'is_active'  : True
        },
        verbose_name="Proprietor",
    )
    shop_photo = models.ImageField(
        upload_to='images/', 
        blank=True
    )
    shop_name = models.CharField(
        max_length=150,
        blank=False,
        null=False,
        verbose_name="Shop Name"
    )
    shop_shortdescribtion = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name= "Short Describtion"
    )
    shop_describtion = models.TextField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name= "Describtion"
    )
    shop_address = models.TextField(
        max_length=500,
        verbose_name="Shop Address"
    )
    shop_gst = models.CharField(
        max_length=15,
        verbose_name="GST NUMBER",
        unique=True
    )
    location = PointField(
        geography=True,
        null=True,
        blank=True
    )
    
    #todo we should make this false once we decide this feature
    is_active = models.BooleanField(
        default= True
    )

    is_job_live = models.BooleanField(
        default=False
    )

    def __str__(self):
        return self.shop_name
    
    class Meta:
        ordering = ('-created_at',)

    

    #todo to implement this feature in the api as well in the admin panel
    def clean(self):
        if self.created_at:
            if ProprietorShop.objects.filter(
                    user_id=self.user_id, 
                    is_active=True,
                    is_job_live = True
                ).exists():
                raise ValidationError(CANNOTPERFORM)
        elif not self.created_at:
            if ProprietorShop.objects.filter(
                        user_id=self.user_id, 
                        is_active=True,
                    ).exists():
                raise ValidationError(SHOPALREADYEXIST)
    
    
class VehicleDeliveryPerson(BaseModel):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to= {
            'user_type' : UserType.b.value[0],
            'is_active'  : True
        },
        verbose_name="DELIVERY-PERSON"
    )
    vehicle_type = models.CharField(
        max_length=2,
        choices=[x.value for x in UserType]
    )
    vehicle_number = models.CharField(
        max_length=10,
        null=True,
        blank=True
    )
    vehicle_name = models.CharField(
        max_length=20,
    )

    #todo if possible we can check the vehicle number in future then tick this true \
    # for now we can have this field default as True

    is_verified = models.BooleanField(
        default=True
    )

    #can have the permission to delete the vehicle and add new if we decide to add this in future
    is_active = models.BooleanField(
        default=True
    )

    is_job_live = models.BooleanField(
        default=False
    )

    def __str__(self):
        return self.vehicle_name
    
    class Meta:
        ordering = ('-created_at',)
    
    