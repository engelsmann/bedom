# Generated by Django 3.2.5 on 2021-07-30 19:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prepare', '0002_alter_fokusgruppe_modul'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='forløb',
            options={'ordering': ['klasse', 'emne'], 'verbose_name_plural': 'forløb'},
        ),
        migrations.AlterModelOptions(
            name='skole',
            options={'ordering': ['navn'], 'verbose_name_plural': 'skoler'},
        ),
        migrations.AlterField(
            model_name='elev',
            name='id',
            field=models.UUIDField(auto_created=True, primary_key=True, serialize=False),
        ),
    ]
