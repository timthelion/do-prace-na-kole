# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-05-11 18:31
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dpnk', '0065_commutemode'),
    ]

    operations = [
        migrations.AddField(
            model_name='trip',
            name='commute_mode_choice',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='dpnk.CommuteMode', verbose_name='Mód dopravy'),
        ),
    ]
