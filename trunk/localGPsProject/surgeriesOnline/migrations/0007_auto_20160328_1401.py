# -*- coding: utf-8 -*-
# Generated by Django 1.9.3 on 2016-03-28 13:01
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('surgeriesOnline', '0006_remove_doctorbooking_details'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doctorappointment',
            name='doctorBooking',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='surgeriesOnline.DoctorBooking'),
        ),
        migrations.AlterField(
            model_name='nurseappointment',
            name='nurseBooking',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='surgeriesOnline.NurseBooking'),
        ),
    ]
