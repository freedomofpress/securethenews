# Generated by Django 2.2.14 on 2020-09-10 21:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0021_scan_onion_available'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scan',
            name='onion_available',
            field=models.NullBooleanField(),
        ),
    ]
