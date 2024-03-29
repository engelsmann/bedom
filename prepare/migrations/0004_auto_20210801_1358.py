# Generated by Django 3.2.5 on 2021-08-01 11:58

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prepare', '0003_auto_20210801_1354'),
    ]

    operations = [
        migrations.AlterField(
            model_name='klasse',
            name='fokus_antal',
            field=models.IntegerField(default=5, help_text='Standardstørrelse af klassens fokusgruppe', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(35)]),
        ),
        migrations.AlterField(
            model_name='klasse',
            name='note',
            field=models.TextField(blank=True, help_text='Lærerens generelle noter om holdet, dets lokale eller historik', max_length=200, null=True),
        ),
    ]
