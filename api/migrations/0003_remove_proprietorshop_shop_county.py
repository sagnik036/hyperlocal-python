# Generated by Django 4.1.4 on 2023-02-05 18:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_proprietorshop_shop_country_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='proprietorshop',
            name='shop_county',
        ),
    ]