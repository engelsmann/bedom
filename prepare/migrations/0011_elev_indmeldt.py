# Generated by Django 3.2.5 on 2021-08-19 17:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prepare', '0010_alter_elev_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='elev',
            name='indmeldt',
            field=models.DateField(blank=True, help_text='Dato for hvornår eleven begynder at gå i klassen', null=True),
        ),
    ]