# Generated by Django 3.2.5 on 2021-07-31 13:26

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('prepare', '0013_auto_20210731_1518'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adfærd',
            name='opdateret',
            field=models.DateTimeField(default=datetime.datetime(2021, 7, 31, 13, 26, 29, 370063, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='adfærd',
            name='oprettet',
            field=models.DateTimeField(default=datetime.datetime(2021, 7, 31, 13, 26, 29, 370015, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='elev',
            name='opdateret',
            field=models.DateTimeField(default=datetime.datetime(2021, 7, 31, 13, 26, 29, 363530, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='elev',
            name='oprettet',
            field=models.DateTimeField(default=datetime.datetime(2021, 7, 31, 13, 26, 29, 363484, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='emne',
            name='opdateret',
            field=models.DateTimeField(default=datetime.datetime(2021, 7, 31, 13, 26, 29, 366989, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='emne',
            name='oprettet',
            field=models.DateTimeField(default=datetime.datetime(2021, 7, 31, 13, 26, 29, 366944, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='fokusgruppe',
            name='opdateret',
            field=models.DateTimeField(default=datetime.datetime(2021, 7, 31, 13, 26, 29, 364713, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='fokusgruppe',
            name='oprettet',
            field=models.DateTimeField(default=datetime.datetime(2021, 7, 31, 13, 26, 29, 364670, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='forløb',
            name='opdateret',
            field=models.DateTimeField(default=datetime.datetime(2021, 7, 31, 13, 26, 29, 368099, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='forløb',
            name='oprettet',
            field=models.DateTimeField(default=datetime.datetime(2021, 7, 31, 13, 26, 29, 368057, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='modul',
            name='opdateret',
            field=models.DateTimeField(default=datetime.datetime(2021, 7, 31, 13, 26, 29, 369141, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='modul',
            name='oprettet',
            field=models.DateTimeField(default=datetime.datetime(2021, 7, 31, 13, 26, 29, 369099, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='video',
            name='opdateret',
            field=models.DateTimeField(default=datetime.datetime(2021, 7, 31, 13, 26, 29, 372995, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='video',
            name='oprettet',
            field=models.DateTimeField(default=datetime.datetime(2021, 7, 31, 13, 26, 29, 372947, tzinfo=utc)),
        ),
    ]