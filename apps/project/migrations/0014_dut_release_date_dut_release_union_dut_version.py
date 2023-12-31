# Generated by Django 4.2.3 on 2023-08-21 09:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0013_project_dev_unit_project_entrust_unit_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='dut',
            name='release_date',
            field=models.DateField(auto_now=True, help_text='发布时间', null=True, verbose_name='发布时间'),
        ),
        migrations.AddField(
            model_name='dut',
            name='release_union',
            field=models.CharField(blank=True, help_text='发布版本', max_length=64, null=True, verbose_name='发布版本'),
        ),
        migrations.AddField(
            model_name='dut',
            name='version',
            field=models.CharField(blank=True, help_text='发布版本', max_length=64, null=True, verbose_name='发布版本'),
        ),
    ]
