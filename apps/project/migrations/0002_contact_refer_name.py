# Generated by Django 4.2.13 on 2024-07-15 16:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='contact',
            name='refer_name',
            field=models.CharField(blank=True, help_text='公司简称', max_length=32, verbose_name='公司简称'),
        ),
    ]
