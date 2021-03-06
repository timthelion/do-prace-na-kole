# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-02-16 18:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dpnk', '0004_auto_20160216_1249'),
    ]

    operations = [
        migrations.CreateModel(
            name='TeamInCampaign',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('dpnk.team',),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='personal_data_opt_in',
            field=models.BooleanField(default=False, verbose_name='Souhlasím se zpracováním osobních údajů podle Zásad o ochraně a zpracování údajů A*M.'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='company_pais_benefitial_fee',
            field=models.BooleanField(default=False, verbose_name='Moje firma si přeje podpořit Auto*Mat a zaplatit benefiční startovné.'),
        ),
    ]
