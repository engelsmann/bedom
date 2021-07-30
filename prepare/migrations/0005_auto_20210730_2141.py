# Generated by Django 3.2.5 on 2021-07-30 19:41

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('prepare', '0004_alter_elev_kaldenavn'),
    ]

    operations = [
        migrations.AlterField(
            model_name='elev',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='elev',
            name='kaldenavn',
            field=models.CharField(blank=True, help_text='Det navn, personen ønsker brugt i daglig tiltale', max_length=15, null=True),
        ),
    ]
