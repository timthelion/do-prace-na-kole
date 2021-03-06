# -*- coding: utf-8 -*-
# Generated by Django 1.9.5.dev20160321164524 on 2016-04-26 14:20
from __future__ import unicode_literals

from django.db import migrations, models
import dpnk.models


class Migration(migrations.Migration):

    dependencies = [
        ('dpnk', '0025_auto_20160412_1238'),
    ]

    operations = [
        migrations.AddField(
            model_name='deliverybatch',
            name='dispatched',
            field=models.BooleanField(default=False, verbose_name='Vyřízeno'),
        ),
        migrations.AlterField(
            model_name='gpxfile',
            name='file',
            field=models.FileField(blank=True, help_text="Zadat trasu nahráním souboru GPX. Pro vytvoření GPX souboru s trasou můžete použít vyhledávání na naší <a href='http://mapa.prahounakole.cz/#hledani' target='_blank'>mapě</a>.", null=True, upload_to=dpnk.models.normalize_gpx_filename, verbose_name='GPX soubor'),
        ),
    ]
