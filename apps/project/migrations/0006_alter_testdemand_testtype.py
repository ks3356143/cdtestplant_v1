# Generated by Django 4.2.3 on 2023-08-02 06:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0005_testdemand_alter_design_demandtype_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testdemand',
            name='testType',
            field=models.CharField(blank=True, default='1', help_text='测试类型', max_length=8, null=True, verbose_name='测试类型'),
        ),
    ]
