# -*- coding: utf-8 -*-
# Generated by Django 1.9.5.dev20160531101208 on 2017-02-20 14:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('t_shirt_delivery', '0004_auto_20170219_1522'),
    ]

    operations = [
        migrations.AddField(
            model_name='subsidiarybox',
            name='dispatched',
            field=models.BooleanField(default=False, verbose_name='Vyřízeno'),
        ),
        migrations.AddField(
            model_name='teampackage',
            name='dispatched',
            field=models.BooleanField(default=False, verbose_name='Vyřízeno'),
        ),
    ]
