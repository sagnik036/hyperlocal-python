# Generated by Django 4.1.4 on 2023-02-05 12:50

import api.models
import base.base_upload_handlers
import base.utils
import ckeditor.fields
from django.conf import settings
import django.contrib.gis.db.models.fields
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('profile_pic', models.ImageField(blank=True, upload_to='images/')),
                ('email', models.EmailField(blank=True, error_messages={'unique': 'A user with that email already exists'}, max_length=254, null=True)),
                ('mobile_number', models.CharField(error_messages={'unique': 'A user with that mobile already exists'}, max_length=50, unique=True)),
                ('is_email_verified', models.BooleanField(default=False)),
                ('is_mobile_verified', models.BooleanField(default=False)),
                ('user_type', models.CharField(blank=True, choices=[('1', 'PROPRIETOR'), ('2', 'DELIVERYPERSON')], max_length=20, null=True)),
                ('is_shop', models.BooleanField(default=False, verbose_name='have shop')),
                ('adhar_photo_front', models.ImageField(upload_to='images/', verbose_name='Adharcard front')),
                ('adhar_photo_back', models.ImageField(upload_to='images/', verbose_name='Adharcard Back')),
                ('is_adhar_verified', models.BooleanField(default=False, verbose_name='AdharCard Verified')),
                ('live_jobs_count', models.PositiveIntegerField(default=0)),
                ('total_jobs_posted', models.PositiveIntegerField(default=0)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'User',
                'verbose_name_plural': 'Users',
                'ordering': ('first_name',),
            },
            managers=[
                ('objects', api.models.CustomUserManager()),
            ],
        ),
        migrations.CreateModel(
            name='AdminContact',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('email', models.EmailField(max_length=254)),
                ('phone_number', models.CharField(max_length=50)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AdminNotification',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=200)),
                ('description', models.CharField(max_length=250)),
                ('sent_to_all', models.BooleanField(default=False)),
                ('recipients', models.ManyToManyField(blank=True, help_text='<b>Note:It will send the notification to the selected user only.</b>', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='FrequentlyAskedQuestion',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('question', models.TextField(max_length=2000)),
                ('answer', models.TextField(max_length=2000)),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='PaymentTerm',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('text', ckeditor.fields.RichTextField()),
                ('document', models.FileField(blank=True, null=True, storage=base.utils.StaticFileStorage(), upload_to=base.base_upload_handlers.handle_payment_term_document, validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf'])])),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PrivacyPolicy',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('text', ckeditor.fields.RichTextField()),
                ('document', models.FileField(blank=True, null=True, storage=base.utils.StaticFileStorage(), upload_to=base.base_upload_handlers.handle_privacy_policy_document, validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf'])])),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TermAndCondition',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('text', ckeditor.fields.RichTextField()),
                ('document', models.FileField(blank=True, null=True, storage=base.utils.StaticFileStorage(), upload_to=base.base_upload_handlers.handle_tnc_document, validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf'])])),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='VehicleDeliveryPerson',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('vehicle_type', models.CharField(choices=[('1', 'PROPRIETOR'), ('2', 'DELIVERYPERSON')], max_length=2)),
                ('vehicle_number', models.CharField(blank=True, max_length=10, null=True)),
                ('vehicle_name', models.CharField(max_length=20)),
                ('is_verified', models.BooleanField(default=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_job_live', models.BooleanField(default=False)),
                ('user', models.ForeignKey(limit_choices_to={'is_active': True, 'user_type': '2'}, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='DELIVERY-PERSON')),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='UserNotification',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('notification_type', models.CharField(choices=[('TNC', 'Terms and conditions updated'), ('PTU', 'Payment terms updated'), ('PPU', 'Privacy policy updated'), ('ADMIN', 'Sent by admin')], max_length=20)),
                ('title', models.CharField(max_length=250)),
                ('body', models.CharField(max_length=500)),
                ('is_read', models.BooleanField(default=False)),
                ('data_id', models.CharField(blank=True, max_length=250, null=True)),
                ('admin_notification', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.adminnotification')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='ProprietorShop',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('shop_photo', models.ImageField(blank=True, upload_to='images/')),
                ('shop_name', models.CharField(max_length=150, verbose_name='Shop Name')),
                ('shop_shortdescribtion', models.CharField(blank=True, max_length=100, null=True, verbose_name='Short Describtion')),
                ('shop_describtion', models.TextField(blank=True, max_length=500, null=True, verbose_name='Describtion')),
                ('shop_address', models.TextField(max_length=500, verbose_name='Shop Address')),
                ('shop_gst', models.CharField(max_length=15, unique=True, verbose_name='GST NUMBER')),
                ('location', django.contrib.gis.db.models.fields.PointField(blank=True, geography=True, null=True, srid=4326)),
                ('is_active', models.BooleanField(default=True)),
                ('is_job_live', models.BooleanField(default=False)),
                ('user', models.ForeignKey(limit_choices_to={'is_active': True, 'user_type': '1'}, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Proprietor')),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='DeviceToken',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('device_type', models.CharField(choices=[('IOS', 'Iphone'), ('ANDROID', 'Android'), ('WEB', 'Web')], max_length=10)),
                ('token', models.TextField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
    ]
