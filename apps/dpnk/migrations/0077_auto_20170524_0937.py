# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-05-24 09:37
from __future__ import unicode_literals

from django.db import migrations, models
import dpnk.models.competition


class Migration(migrations.Migration):

    dependencies = [
        ('dpnk', '0076_auto_20170514_2202'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='anonymize',
            field=models.BooleanField(default=False, verbose_name='Anonimizovat položky na faktuře'),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='wp_api_url',
            field=models.URLField(blank=True, default='http://www.dopracenakole.cz', null=True, verbose_name='Adresa pro Wordpress API se články'),
        ),
        migrations.AlterField(
            model_name='competition',
            name='commute_modes',
            field=models.ManyToManyField(blank=True, default=dpnk.models.competition.default_commute_modes, help_text='Můžete vybrat víc položek pomocí klávesy shift. Většina soutěží je vypsána jako kolo + chůze/běh', to='dpnk.CommuteMode', verbose_name='Počítané módy dopravy'),
        ),
        migrations.AlterField(
            model_name='competition',
            name='is_public',
            field=models.BooleanField(default=True, help_text='Zobrazovat v přehledech soutěží a výsledků?', verbose_name='Soutěž je veřejná'),
        ),
        migrations.AlterField(
            model_name='competition',
            name='show_results',
            field=models.BooleanField(default=True, help_text='Povolit možnost prohlížet výsledky soutěže.', verbose_name='Zobrazovat výsledky soutěže'),
        ),
    ]