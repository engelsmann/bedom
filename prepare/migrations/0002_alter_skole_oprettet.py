# Generated by Django 3.2.5 on 2021-08-01 11:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prepare', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='skole',
            name='oprettet',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
