# Generated by Django 2.0.9 on 2019-04-10 16:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dpnk', '0129_auto_20190403_2010'),
    ]

    operations = [
        migrations.AddField(
            model_name='commutemode',
            name='icon_html',
            field=models.TextField(default='', verbose_name='Html of summary icon'),
        ),
    ]