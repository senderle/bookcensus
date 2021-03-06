# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-03-09 20:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('census', '0002_auto_20180305_2022'),
    ]

    operations = [
        migrations.AlterField(
            model_name='copy',
            name='Height',
            field=models.FloatField(default=0, null=True),
        ),
        migrations.AlterField(
            model_name='copy',
            name='Width',
            field=models.FloatField(default=0, null=True),
        ),
        migrations.AlterField(
            model_name='issue',
            name='DEEP',
            field=models.CharField(blank=True, default='', max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='issue',
            name='notes',
            field=models.CharField(blank=True, default='', max_length=1000, null=True),
        ),
    ]
