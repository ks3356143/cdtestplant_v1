# -*- coding: utf-8 -*-
"""
剩余信息清理定时任务（GB/T 28452-2012 第三级 7.1.8 c/f）

把文档生成过程的临时中间产物按保留期清掉。可由操作系统的计划任务定期调用：

    python manage.py purge_residue --hours 24

默认保留 24 小时；传 --hours 0 表示全部清理。
"""
from django.core.management.base import BaseCommand

from apps.system.tools.residue import purge_temp_files


class Command(BaseCommand):
    help = '清理过期的临时文件（剩余信息保护，7.1.8）'

    def add_arguments(self, parser):
        parser.add_argument('--hours', type=int, default=24,
                            help='保留期（小时），0 表示全部清理，默认 24')

    def handle(self, *args, **options):
        hours = max(0, options['hours'])
        result = purge_temp_files(max_age_hours=hours)
        self.stdout.write(self.style.SUCCESS(
            f"剩余信息清理完成：扫描 {result['scanned']} 个临时文件，删除 {result['removed']} 个"
            f"（释放 {result['freed_mb']} MB），跳过占用中 {result['failed']} 个，保留期 {hours} 小时"
        ))
