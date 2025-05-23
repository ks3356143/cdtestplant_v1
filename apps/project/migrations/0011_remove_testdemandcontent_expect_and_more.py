# Generated by Django 5.2 on 2025-04-17 14:57

import django.db.models.deletion
import shortuuidfield.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0010_remove_testdemandcontent_condition_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='testdemandcontent',
            name='expect',
        ),
        migrations.RemoveField(
            model_name='testdemandcontent',
            name='operation',
        ),
        migrations.CreateModel(
            name='TestDemandContentStep',
            fields=[
                ('remark', models.CharField(blank=True, help_text='描述', max_length=255, null=True, verbose_name='描述')),
                ('update_datetime', models.DateField(auto_now=True, help_text='修改时间', null=True, verbose_name='修改时间')),
                ('create_datetime', models.DateField(auto_now_add=True, help_text='创建时间', null=True, verbose_name='创建时间')),
                ('sort', models.IntegerField(blank=True, default=1, help_text='显示排序', null=True, verbose_name='显示排序')),
                ('id', shortuuidfield.fields.ShortUUIDField(blank=True, editable=False, help_text='Id', max_length=22, primary_key=True, serialize=False, verbose_name='Id')),
                ('operation', models.CharField(blank=True, max_length=3072, null=True, verbose_name='测试子项操作')),
                ('expect', models.CharField(blank=True, max_length=1024, null=True, verbose_name='期望')),
                ('testDemandContent', models.ForeignKey(db_constraint=False, help_text='归属的测试项', on_delete=django.db.models.deletion.CASCADE, related_name='testStepField', related_query_name='testStepField', to='project.testdemandcontent', verbose_name='归属的测试项')),
            ],
            options={
                'verbose_name': '核心模型',
                'verbose_name_plural': '核心模型',
                'abstract': False,
            },
        ),
    ]
