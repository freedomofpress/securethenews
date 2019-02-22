# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-16 22:34
from __future__ import unicode_literals

from django.db import migrations, models
import wagtail.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0002_create_homepage'),
    ]

    operations = [
        migrations.AddField(
            model_name='homepage',
            name='how_body',
            field=wagtail.core.fields.RichTextField(default='Blah blah'),
        ),
        migrations.AddField(
            model_name='homepage',
            name='how_header',
            field=models.CharField(default='Switching to HTTPS is easier than ever', max_length=50),
        ),
        migrations.AddField(
            model_name='homepage',
            name='main_title',
            field=models.CharField(default='Every news site should be secure.', max_length=50),
        ),
        migrations.AddField(
            model_name='homepage',
            name='sub_title',
            field=models.CharField(default="It's critical for both journalists and readers.", max_length=50),
        ),
        migrations.AddField(
            model_name='homepage',
            name='why_body',
            field=wagtail.core.fields.RichTextField(default='Blah blah'),
        ),
        migrations.AddField(
            model_name='homepage',
            name='why_header',
            field=models.CharField(default='Encryption protects your readers', max_length=50),
        ),
    ]
