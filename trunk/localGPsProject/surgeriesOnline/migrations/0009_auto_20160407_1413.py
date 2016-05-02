# -*- coding: utf-8 -*-
# Generated by Django 1.9.3 on 2016-04-07 13:13
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('surgeriesOnline', '0008_auto_20160404_2245'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='specializedfacility',
            name='email',
        ),
        migrations.AddField(
            model_name='specializedfacility',
            name='user',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
