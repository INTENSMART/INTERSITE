# Generated by Django 4.0.1 on 2022-05-18 05:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administrateur', '0009_delete_modeladministrateur'),
    ]

    operations = [
        migrations.AlterField(
            model_name='modeletablissement',
            name='telephone',
            field=models.IntegerField(blank=True, max_length=9, null=True),
        ),
    ]
