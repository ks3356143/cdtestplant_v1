# Generated by Django 4.2.11 on 2024-04-15 10:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0005_alter_operationlog_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='operationlog',
            name='operate_obj',
            field=models.CharField(default='未关联对象', help_text='操作对象', max_length=256, verbose_name='操作对象'),
        ),
    ]
