# Generated by Django 4.2.3 on 2023-08-17 05:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dict', '0004_alter_dictitem_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dictitem',
            name='status',
            field=models.CharField(blank=True, default='1', help_text='状态', max_length=8, null=True, verbose_name='状态'),
        ),
    ]