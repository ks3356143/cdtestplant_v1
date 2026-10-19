# -*- coding: utf-8 -*-
"""
定时增量备份（GB/T 28452-2012 第三级 7.1.9 b) 增量信息备份与恢复）

由操作系统的计划任务定期调用即可实现"系统定时对新增信息进行备份"：

    python manage.py auto_backup                 # 全部业务数据，增量
    python manage.py auto_backup --kind full     # 改跑全量
    python manage.py auto_backup --project 42    # 只备份某个项目

Windows 计划任务示例（每天 02:00）：
    schtasks /create /tn "cdtestplant-增量备份" /tr "python manage.py auto_backup" /sc daily /st 02:00
"""
from django.core.management.base import BaseCommand

from apps.system.tools.backup import BACKUP_MODELS, create_backup


class Command(BaseCommand):
    help = '执行一次定时备份（默认增量、全部业务数据），供计划任务调用'

    def add_arguments(self, parser):
        parser.add_argument('--kind', choices=('full', 'incremental'), default='incremental',
                            help='备份类型，默认增量')
        parser.add_argument('--project', type=int, default=None, help='只备份指定项目 id')
        parser.add_argument('--name', default='', help='备份名称，留空自动生成')

    def handle(self, *args, **options):
        kind = options['kind']
        project_id = options['project']
        record, table_stats = create_backup(kind, project_id, options['name'] or '', None)
        self.stdout.write(self.style.SUCCESS(
            f"备份完成：{record.name}（{record.get_kind_display()} / {record.scope_label}），"
            f"覆盖 {len(table_stats)} 张表共 {record.record_count} 条数据，"
            f"文件 {record.file_name}，SHA-256 {record.digest[:16]}…"
        ))
        self.stdout.write(f'纳入备份的业务表共 {len(BACKUP_MODELS)} 张')
