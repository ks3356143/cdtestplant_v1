from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0004_auditlog_index'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataIntegrityTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('table_name', models.CharField(help_text='project_case 等 db_table', max_length=64, verbose_name='受保护表')),
                ('object_id', models.CharField(max_length=32, verbose_name='数据行 id')),
                ('digest', models.CharField(help_text='关键字段排序 JSON 快照的 SHA256', max_length=64, verbose_name='完整性摘要(SHA256)')),
                ('algorithm', models.CharField(default='SHA256', max_length=16, verbose_name='算法')),
                ('update_datetime', models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name='标签更新时间')),
                ('create_datetime', models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name='创建时间')),
            ],
            options={
                'verbose_name': '数据完整性标签',
                'verbose_name_plural': '数据完整性标签',
                'db_table': 'system_data_integrity_tag',
                'unique_together': {('table_name', 'object_id')},
            },
        ),
    ]
