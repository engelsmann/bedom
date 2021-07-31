# Generated by Django 3.2.5 on 2021-07-31 10:30

import django.core.validators
from django.db import migrations, models
import django.db.models.functions.math


class Migration(migrations.Migration):

    dependencies = [
        ('prepare', '0006_alter_elev_note'),
    ]

    operations = [
        migrations.AlterField(
            model_name='elev',
            name='efternavn',
            field=models.CharField(help_text='Personens officielle efternavn(e) som i protokol', max_length=50, validators=[django.core.validators.MinLengthValidator(2)]),
        ),
        migrations.AlterField(
            model_name='elev',
            name='fornavn',
            field=models.CharField(help_text='Personens officielle fornavn(e) som i protokol', max_length=50, validators=[django.core.validators.MinLengthValidator(2)]),
        ),
        migrations.AlterField(
            model_name='emne',
            name='note',
            field=models.TextField(blank=True, help_text='Lærerens krav til og ambitioner for emnet', max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name='fokusgruppe',
            name='rand_rank',
            field=models.FloatField(default=django.db.models.functions.math.Random(), editable=False, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(1.0)]),
        ),
        migrations.AlterField(
            model_name='forløb',
            name='kommentar',
            field=models.TextField(blank=True, help_text='Præsentation til holdets elever af det konkrete forløb i klassen', max_length=500, null=True),
        ),
    ]