# Generated by Django 4.2.9 on 2024-02-27 05:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0021_abbreviation'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='abbreviation',
            field=models.JSONField(blank=True, default=[], help_text='缩略语', null=True, verbose_name='缩略语'),
        ),
    ]
