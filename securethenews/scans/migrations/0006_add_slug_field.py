# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-09-13 04:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scans', '0005_auto_20160803_2254'),
    ]

    operations = [
        migrations.AddField(
            model_name='site',
            name='slug',
            field=models.SlugField(default='', verbose_name='Slug'),
        ),
    ]
