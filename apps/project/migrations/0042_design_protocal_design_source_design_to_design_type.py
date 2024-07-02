# Generated by Django 4.2.13 on 2024-06-24 09:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0041_alter_problem_closemethod_alter_project_abbreviation_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='design',
            name='protocal',
            field=models.CharField(blank=True, default='', help_text='接口协议', max_length=64, null=True, verbose_name='接口协议'),
        ),
        migrations.AddField(
            model_name='design',
            name='source',
            field=models.CharField(blank=True, default='', help_text='接口来源', max_length=64, null=True, verbose_name='接口来源'),
        ),
        migrations.AddField(
            model_name='design',
            name='to',
            field=models.CharField(blank=True, default='', help_text='接口目的地', max_length=64, null=True, verbose_name='接口目的地'),
        ),
        migrations.AddField(
            model_name='design',
            name='type',
            field=models.CharField(blank=True, default='', help_text='接口类型', max_length=64, null=True, verbose_name='接口类型'),
        ),
    ]