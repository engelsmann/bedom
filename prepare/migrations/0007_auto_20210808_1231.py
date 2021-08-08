# Generated by Django 3.2.5 on 2021-08-08 10:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prepare', '0006_auto_20210801_1550'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fokusgruppe',
            name='bedømt',
            field=models.BooleanField(default='', null=True),
        ),
        migrations.AlterField(
            model_name='fokusgruppe',
            name='faglig',
            field=models.IntegerField(help_text='Score for elevens evne til at bidrage til en faglig samtale', null=True),
        ),
        migrations.AlterField(
            model_name='fokusgruppe',
            name='hjælp',
            field=models.IntegerField(help_text='Score for elevens evne til at yde hjælp til faglig problemløsning', null=True),
        ),
        migrations.AlterField(
            model_name='fokusgruppe',
            name='modul',
            field=models.ManyToManyField(default='', to='prepare.Modul'),
        ),
        migrations.AlterField(
            model_name='fokusgruppe',
            name='spørg',
            field=models.IntegerField(help_text='Score for elevens evne til at søge hjælp på fagligt spørgsmål', null=True),
        ),
        migrations.AlterField(
            model_name='fokusgruppe',
            name='stikord',
            field=models.CharField(help_text='Lærerens observationer i "tre" ord', max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='fokusgruppe',
            name='tilstede',
            field=models.BooleanField(default='', null=True),
        ),
        migrations.AlterField(
            model_name='modul',
            name='afholdt',
            field=models.DateField(help_text='Planlagt / faktisk dato for modulet'),
        ),
    ]
