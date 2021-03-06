# Generated by Django 2.0.1 on 2018-03-01 10:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dpnk', '0089_auto_20180227_1112'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='competition',
            name='company_competitors',
        ),
        migrations.RemoveField(
            model_name='competition',
            name='team_competitors',
        ),
        migrations.RemoveField(
            model_name='competition',
            name='user_attendance_competitors',
        ),
        migrations.RemoveField(
            model_name='competition',
            name='without_admission',
        ),
        migrations.AlterField(
            model_name='competition',
            name='mandatory',
            field=models.BooleanField(default=False, help_text='Dotazník je potřeba vyplnit před tím, než je možné zadávat jízdy', verbose_name='Povinný dotazník'),
        ),
    ]
