# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-08 15:42
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
import stdnumfield.models


class Migration(migrations.Migration):

    dependencies = [
        ('dpnk', '0085_auto_20170906_1052'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='invoice_xml',
            field=models.FileField(blank=True, max_length=512, null=True, upload_to='invoices', verbose_name='XML faktury'),
        ),
        migrations.AlterField(
            model_name='company',
            name='dic',
            field=stdnumfield.models.StdNumField(alphabets=[None], blank=True, default='', error_messages={'stdnum_format': 'DIČ není zadáno ve správném formátu. Zkontrolujte že číslo má osm číslic a případně ho doplňte nulami zleva. Číslu musí předcházet dvě písmena identifikátoru země (např. CZ)'}, formats=['cz.dic'], null=True, validators=[django.core.validators.RegexValidator('^[a-zA-Z]{2}[0-9]*$', 'DIČ musí být číslo uvozené dvoupísmeným identifikátorem státu.')], verbose_name='DIČ'),
        ),
        migrations.AlterField(
            model_name='company',
            name='ico',
            field=stdnumfield.models.StdNumField(alphabets=[None], blank=True, default=None, error_messages={'stdnum_format': 'IČO není zadáno ve správném formátu. Zkontrolujte že číslo má osm číslic a případně ho doplňte nulami zleva.'}, formats=['cz.dic'], help_text='Pokud má vaše organizace IČO, prosím vyplňte, jinak nechte prázdné.', null=True, validators=[django.core.validators.RegexValidator('^[0-9]*$', 'IČO musí být číslo')], verbose_name='IČO'),
        ),
    ]
