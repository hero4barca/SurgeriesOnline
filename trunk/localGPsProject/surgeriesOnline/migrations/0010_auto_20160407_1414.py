# -*- coding: utf-8 -*-
# Generated by Django 1.9.3 on 2016-04-07 13:14
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('surgeriesOnline', '0009_auto_20160407_1413'),
    ]

    operations = [
        migrations.AlterField(
            model_name='specializedfacility',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
