# Generated by Django 4.2.13 on 2024-07-24 14:43

import apps.dict.fragment.enums
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0003_alter_design_protocal'),
        ('dict', '0002_userdictfield'),
    ]

    operations = [
        migrations.CreateModel(
            name='Fragment',
            fields=[
                ('id', models.BigAutoField(help_text='Id', primary_key=True, serialize=False, verbose_name='Id')),
                ('remark', models.CharField(blank=True, help_text='描述', max_length=255, null=True, verbose_name='描述')),
                ('update_datetime', models.DateField(auto_now=True, help_text='修改时间', null=True, verbose_name='修改时间')),
                ('create_datetime', models.DateField(auto_now_add=True, help_text='创建时间', null=True, verbose_name='创建时间')),
                ('sort', models.IntegerField(blank=True, default=1, help_text='显示排序', null=True, verbose_name='显示排序')),
                ('name', models.CharField(max_length=128, verbose_name='片段名称-必须和文件名一致')),
                ('belong_doc', models.PositiveSmallIntegerField(choices=[(1, apps.dict.fragment.enums.DocNameEnum['dg']), (2, apps.dict.fragment.enums.DocNameEnum['sm']), (3, apps.dict.fragment.enums.DocNameEnum['jl']), (4, apps.dict.fragment.enums.DocNameEnum['hsm']), (5, apps.dict.fragment.enums.DocNameEnum['hjl']), (6, apps.dict.fragment.enums.DocNameEnum['bg']), (7, apps.dict.fragment.enums.DocNameEnum['wtd'])], verbose_name='所属文档')),
                ('field_seq', models.CharField(max_length=64, verbose_name='用户字段表的顺序')),
                ('is_main', models.BooleanField(default=False, verbose_name='是否替换磁盘的片段')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='frag', related_query_name='qFrag', to='project.project')),
            ],
            options={
                'verbose_name': '文档片段',
                'verbose_name_plural': '文档片段',
                'db_table': 'fragment_core',
                'ordering': ('-create_datetime', '-id'),
            },
        ),
        migrations.CreateModel(
            name='PictureField',
            fields=[
                ('id', models.BigAutoField(help_text='Id', primary_key=True, serialize=False, verbose_name='Id')),
                ('remark', models.CharField(blank=True, help_text='描述', max_length=255, null=True, verbose_name='描述')),
                ('update_datetime', models.DateField(auto_now=True, help_text='修改时间', null=True, verbose_name='修改时间')),
                ('create_datetime', models.DateField(auto_now_add=True, help_text='创建时间', null=True, verbose_name='创建时间')),
                ('sort', models.IntegerField(blank=True, default=1, help_text='显示排序', null=True, verbose_name='显示排序')),
                ('name', models.CharField(max_length=64, verbose_name='字段名称-字母')),
                ('img', models.ImageField(upload_to='field_images', verbose_name='图片')),
                ('frag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='uPFeild', related_query_name='uPQField', to='dict.fragment')),
            ],
            options={
                'verbose_name': '图片',
                'verbose_name_plural': '图片',
                'db_table': 'fragment_field_picture',
                'ordering': ('-create_datetime', '-id'),
            },
        ),
        migrations.CreateModel(
            name='TableField',
            fields=[
                ('id', models.BigAutoField(help_text='Id', primary_key=True, serialize=False, verbose_name='Id')),
                ('remark', models.CharField(blank=True, help_text='描述', max_length=255, null=True, verbose_name='描述')),
                ('update_datetime', models.DateField(auto_now=True, help_text='修改时间', null=True, verbose_name='修改时间')),
                ('create_datetime', models.DateField(auto_now_add=True, help_text='创建时间', null=True, verbose_name='创建时间')),
                ('sort', models.IntegerField(blank=True, default=1, help_text='显示排序', null=True, verbose_name='显示排序')),
                ('name', models.CharField(max_length=64, verbose_name='字段名称-字母')),
                ('headers', models.CharField(blank=True, max_length=1024, null=True, verbose_name='表头')),
                ('text', models.TextField(blank=True, null=True)),
                ('frag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='uBFeild', related_query_name='uBQField', to='dict.fragment')),
            ],
            options={
                'verbose_name': '图片',
                'verbose_name_plural': '图片',
                'db_table': 'fragment_field_table',
                'ordering': ('-create_datetime', '-id'),
            },
        ),
        migrations.CreateModel(
            name='TextField',
            fields=[
                ('id', models.BigAutoField(help_text='Id', primary_key=True, serialize=False, verbose_name='Id')),
                ('remark', models.CharField(blank=True, help_text='描述', max_length=255, null=True, verbose_name='描述')),
                ('update_datetime', models.DateField(auto_now=True, help_text='修改时间', null=True, verbose_name='修改时间')),
                ('create_datetime', models.DateField(auto_now_add=True, help_text='创建时间', null=True, verbose_name='创建时间')),
                ('sort', models.IntegerField(blank=True, default=1, help_text='显示排序', null=True, verbose_name='显示排序')),
                ('name', models.CharField(max_length=64, verbose_name='字段名称-字母')),
                ('text', models.TextField(verbose_name='多行文本段落')),
                ('frag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='uTFeild', related_query_name='uTQField', to='dict.fragment')),
            ],
            options={
                'verbose_name': '储存当行文本',
                'verbose_name_plural': '储存当行文本',
                'db_table': 'fragment_field_text',
                'ordering': ('-create_datetime', '-id'),
            },
        ),
        migrations.CreateModel(
            name='WordField',
            fields=[
                ('id', models.BigAutoField(help_text='Id', primary_key=True, serialize=False, verbose_name='Id')),
                ('remark', models.CharField(blank=True, help_text='描述', max_length=255, null=True, verbose_name='描述')),
                ('update_datetime', models.DateField(auto_now=True, help_text='修改时间', null=True, verbose_name='修改时间')),
                ('create_datetime', models.DateField(auto_now_add=True, help_text='创建时间', null=True, verbose_name='创建时间')),
                ('sort', models.IntegerField(blank=True, default=1, help_text='显示排序', null=True, verbose_name='显示排序')),
                ('name', models.CharField(max_length=64, verbose_name='字段名称-字母')),
                ('word', models.CharField(max_length=1024, verbose_name='单行文本')),
                ('frag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='uWFeild', related_query_name='uWQField', to='dict.fragment')),
            ],
            options={
                'verbose_name': '储存当行文本',
                'verbose_name_plural': '储存当行文本',
                'db_table': 'fragment_field_word',
                'ordering': ('-create_datetime', '-id'),
            },
        ),
        migrations.DeleteModel(
            name='UserDictField',
        ),
        migrations.AddConstraint(
            model_name='fragment',
            constraint=models.UniqueConstraint(fields=('name', 'belong_doc'), name='unique_name_belong_doc'),
        ),
    ]
