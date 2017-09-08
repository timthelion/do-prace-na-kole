# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-05 11:21
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations
import stdnumfield.models


class Migration(migrations.Migration):

    dependencies = [
        ('dpnk', '0083_remove_userprofile_personal_data_opt_in'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='dic',
            field=stdnumfield.models.StdNumField(alphabets=[None], blank=True, default='', formats=['cz.dic'], null=True, verbose_name='DIČ'),
        ),
        migrations.AlterField(
            model_name='company',
            name='ico',
            field=stdnumfield.models.StdNumField(alphabets=[None], blank=True, default=None, formats=['cz.dic'], help_text='Pokud má vaše organizace IČO, prosím vyplňte, jinak nechte prázdné.', null=True, validators=[django.core.validators.RegexValidator('^[0-9]*$', 'IČO musí být číslo')], verbose_name='IČO'),
        ),
    ]
