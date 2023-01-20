# Generated by Django 4.1.4 on 2023-01-20 15:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0013_proprietorshop'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proprietorshop',
            name='lat',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
        ),
        migrations.AlterField(
            model_name='proprietorshop',
            name='long',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
        ),
        migrations.AlterField(
            model_name='proprietorshop',
            name='shop_describtion',
            field=models.TextField(blank=True, max_length=500, null=True, verbose_name='Describtion'),
        ),
    ]