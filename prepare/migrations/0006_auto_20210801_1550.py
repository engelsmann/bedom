# Generated by Django 3.2.5 on 2021-08-01 13:50

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prepare', '0005_auto_20210801_1520'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='adfærd',
            options={},
        ),
        migrations.RemoveField(
            model_name='adfærd',
            name='faglig',
        ),
        migrations.RemoveField(
            model_name='adfærd',
            name='fokusgruppe',
        ),
        migrations.RemoveField(
            model_name='adfærd',
            name='hjælp',
        ),
        migrations.RemoveField(
            model_name='adfærd',
            name='modul',
        ),
        migrations.RemoveField(
            model_name='adfærd',
            name='opdateret',
        ),
        migrations.RemoveField(
            model_name='adfærd',
            name='oprettet',
        ),
        migrations.RemoveField(
            model_name='adfærd',
            name='reaktion',
        ),
        migrations.RemoveField(
            model_name='adfærd',
            name='spørg',
        ),
        migrations.RemoveField(
            model_name='adfærd',
            name='stikord',
        ),
        migrations.RemoveField(
            model_name='adfærd',
            name='tilstede',
        ),
        migrations.AddField(
            model_name='fokusgruppe',
            name='faglig',
            field=models.IntegerField(help_text='Score for elevens evne til at bidrage til en faglig samtale', null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(4)]),
        ),
        migrations.AddField(
            model_name='fokusgruppe',
            name='hjælp',
            field=models.IntegerField(help_text='Score for elevens evne til at yde hjælp til faglig problemløsning', null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(4)]),
        ),
        migrations.AddField(
            model_name='fokusgruppe',
            name='reaktion',
            field=models.CharField(help_text='Elevens bemærkning', max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='fokusgruppe',
            name='spørg',
            field=models.IntegerField(help_text='Score for elevens evne til at søge hjælp på fagligt spørgsmål', null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(4)]),
        ),
        migrations.AddField(
            model_name='fokusgruppe',
            name='stikord',
            field=models.CharField(help_text='Lærerens observationer i ord', max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='fokusgruppe',
            name='tilstede',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='adfærd',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='fokusgruppe',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False, verbose_name='Fokusgruppe-kandidatens elev+modul-løbenummer'),
        ),
    ]
