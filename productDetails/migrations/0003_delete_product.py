# Generated by Django 4.1.4 on 2022-12-17 15:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('productDetails', '0002_products'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Product',
        ),
    ]