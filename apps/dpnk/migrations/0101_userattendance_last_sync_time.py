# Generated by Django 2.0.4 on 2018-05-17 22:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dpnk', '0100_auto_20180514_1504'),
    ]

    operations = [
        migrations.AddField(
            model_name='userattendance',
            name='last_sync_time',
            field=models.DateTimeField(default=None, null=True, verbose_name='Poslední synchronizace'),
        ),
    ]