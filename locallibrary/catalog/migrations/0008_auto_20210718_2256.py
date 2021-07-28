# Generated by Django 3.1.2 on 2021-07-18 20:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0007_auto_20210714_0924'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='book',
            options={},
        ),
        migrations.AlterModelOptions(
            name='bookinstance',
            options={'ordering': ['due_back'], 'permissions': [('can_identify_borrower', 'View borrower identity'), ('can_mark_returned', 'Mark as returned')]},
        ),
    ]