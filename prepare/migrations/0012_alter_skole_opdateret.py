# Generated by Django 3.2.5 on 2021-07-31 11:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prepare', '0011_auto_20210731_1354'),
    ]

    operations = [
        migrations.AlterField(
            model_name='skole',
            name='opdateret',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
