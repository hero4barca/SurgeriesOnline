# -*- coding: utf-8 -*-
# Generated by Django 1.9.3 on 2016-03-21 20:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('surgeriesOnline', '0002_auto_20160316_1739'),
    ]

    operations = [
        migrations.AddField(
            model_name='doctorappointment',
            name='status',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='nurseappointment',
            name='status',
            field=models.IntegerField(default=0),
        ),
    ]