# Generated by Django 4.1.4 on 2022-12-18 12:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('productDetails', '0003_delete_product'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Products',
            new_name='Product',
        ),
    ]