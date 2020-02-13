# -*- coding: utf-8 -*-
# Generated by Django 1.11.dev20161107131156 on 2016-12-19 16:13
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('coupons', '0002_auto_20161219_1621'),
        ('dpnk', '0043_auto_20161219_1512'),
    ]

    operations = [
        migrations.AddField(
            model_name='userattendance',
            name='discount_coupon',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='coupons.DiscountCoupon', verbose_name='Slevový kupón'),
        ),
        migrations.AlterField(
            model_name='commontransaction',
            name='transaction_ptr',
            field=models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, to='dpnk.Transaction'),
        ),
        migrations.AlterField(
            model_name='packagetransaction',
            name='transaction_ptr',
            field=models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, to='dpnk.Transaction'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='transaction_ptr',
            field=models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, to='dpnk.Transaction'),
        ),
        migrations.AlterField(
            model_name='useractiontransaction',
            name='transaction_ptr',
            field=models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, to='dpnk.Transaction'),
        ),
    ]