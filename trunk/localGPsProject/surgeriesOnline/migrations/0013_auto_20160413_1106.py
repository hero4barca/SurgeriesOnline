# -*- coding: utf-8 -*-
# Generated by Django 1.9.3 on 2016-04-13 10:06
from __future__ import unicode_literals

from django.db import migrations
import fernet_fields.fields


class Migration(migrations.Migration):

    dependencies = [
        ('surgeriesOnline', '0012_patienttransfer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doctorappointment',
            name='details',
            field=fernet_fields.fields.EncryptedTextField(),
        ),
    ]
