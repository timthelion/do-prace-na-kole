# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-05-12 11:19
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dpnk', '0067_populate_commute_mode'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='commutemode',
            options={'ordering': ['order'], 'verbose_name': 'Mód dopravy', 'verbose_name_plural': 'Módy dopravy'},
        ),
        migrations.RemoveField(
            model_name='trip',
            name='commute_mode',
        ),
    ]