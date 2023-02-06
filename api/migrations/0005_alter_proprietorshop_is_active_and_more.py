# Generated by Django 4.1.4 on 2023-02-06 20:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_alter_vehicledeliveryperson_vehicle_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proprietorshop',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='IS ACTIVE'),
        ),
        migrations.AlterField(
            model_name='proprietorshop',
            name='is_job_live',
            field=models.BooleanField(default=False, verbose_name='IS JOB LIVE'),
        ),
        migrations.AlterField(
            model_name='vehicledeliveryperson',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='IS ACTIVE'),
        ),
        migrations.AlterField(
            model_name='vehicledeliveryperson',
            name='is_job_live',
            field=models.BooleanField(default=False, verbose_name='IS JOB LIVE'),
        ),
        migrations.AlterField(
            model_name='vehicledeliveryperson',
            name='is_verified',
            field=models.BooleanField(default=True, verbose_name='IS VERIFIED'),
        ),
    ]