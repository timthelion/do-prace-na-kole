# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-05-14 22:02
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import dpnk.models.gpxfile


class Migration(migrations.Migration):

    dependencies = [
        ('dpnk', '0075_populate_competition_modes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gpxfile',
            name='file',
            field=models.FileField(blank=True, help_text="Zadat trasu nahráním souboru GPX. Pro vytvoření GPX souboru s trasou můžete použít vyhledávání na naší <a href='http://mapa.prahounakole.cz/#hledani' target='_blank'>mapě</a>.", max_length=512, null=True, upload_to=dpnk.models.gpxfile.normalize_gpx_filename, verbose_name='GPX soubor'),
        ),
        migrations.AlterField(
            model_name='trip',
            name='commute_mode',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='dpnk.CommuteMode', verbose_name='Dopravní prostředek'),
        ),
    ]
