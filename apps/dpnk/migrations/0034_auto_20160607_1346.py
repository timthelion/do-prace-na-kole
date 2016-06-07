# -*- coding: utf-8 -*-
# Generated by Django 1.9.5.dev20160531101208 on 2016-06-07 13:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dpnk', '0033_auto_20160607_1132'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='invoice',
            options={'ordering': ('sequence_number', 'campaign'), 'verbose_name': 'Faktura', 'verbose_name_plural': 'Faktury'},
        ),
        migrations.AddField(
            model_name='competitionresult',
            name='result_divident',
            field=models.FloatField(blank=True, default=None, null=True, verbose_name='Dělenec'),
        ),
        migrations.AddField(
            model_name='competitionresult',
            name='result_divisor',
            field=models.FloatField(blank=True, default=None, null=True, verbose_name='Dělitel'),
        ),
    ]
