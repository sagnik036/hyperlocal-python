# Generated by Django 4.1.4 on 2023-01-29 12:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_proprietorshop_is_job_live_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proprietorshop',
            name='user',
            field=models.ForeignKey(error_messages={'unique': 'Shop already exists for this user.'}, limit_choices_to={'is_active': True, 'user_type': '1'}, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Proprietor'),
        ),
    ]
