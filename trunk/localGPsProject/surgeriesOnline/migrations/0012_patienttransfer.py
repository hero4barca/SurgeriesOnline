# -*- coding: utf-8 -*-
# Generated by Django 1.9.3 on 2016-04-11 11:54
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('surgeriesOnline', '0011_auto_20160408_1345'),
    ]

    operations = [
        migrations.CreateModel(
            name='PatientTransfer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('requestDate', models.DateField()),
                ('transferStatus', models.BooleanField(default=False)),
                ('approvalDate', models.DateField(null=True)),
                ('approve', models.NullBooleanField()),
                ('transferDate', models.DateField(null=True)),
                ('fromSurgery', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='from_surgery', to='surgeriesOnline.Surgery')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='surgeriesOnline.Patient')),
                ('toSurgery', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='to_surgery', to='surgeriesOnline.Surgery')),
            ],
        ),
    ]