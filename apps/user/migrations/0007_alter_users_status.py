# Generated by Django 4.2.11 on 2024-04-22 18:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0006_alter_operationlog_operate_obj'),
    ]

    operations = [
        migrations.AlterField(
            model_name='users',
            name='status',
            field=models.CharField(default='1', help_text='status', max_length=15, verbose_name='启用状态'),
        ),
    ]