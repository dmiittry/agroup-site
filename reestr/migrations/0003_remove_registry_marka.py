# Generated by Django 5.2.1 on 2025-05-29 08:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reestr', '0002_alter_registry_marka'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='registry',
            name='marka',
        ),
    ]
