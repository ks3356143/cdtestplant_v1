# Generated by Django 4.2.3 on 2023-08-21 10:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0014_dut_release_date_dut_release_union_dut_version'),
    ]

    operations = [
        migrations.AddField(
            model_name='design',
            name='chapter',
            field=models.CharField(blank=True, help_text='设计需求章节号', max_length=64, verbose_name='设计需求章节号'),
        ),
    ]