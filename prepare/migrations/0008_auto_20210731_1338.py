# Generated by Django 3.2.5 on 2021-07-31 11:38

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prepare', '0007_auto_20210731_1230'),
    ]

    operations = [
        migrations.AddField(
            model_name='skole',
            name='opdateret',
            field=models.DateTimeField(default=datetime.datetime(2021, 7, 31, 13, 38, 52, 755631)),
        ),
        migrations.AddField(
            model_name='skole',
            name='oprettet',
            field=models.DateTimeField(default=datetime.datetime(2021, 7, 31, 13, 38, 52, 755569)),
        ),
    ]