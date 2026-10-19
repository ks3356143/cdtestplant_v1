# -*- coding: utf-8 -*-
"""
apps/system 单元测试 —— 覆盖 GB/T 28452-2012 第三级新增能力

- 备份与故障恢复（7.1.9）：采集范围、摘要校验、篡改拒绝、按主键恢复
- 安全性检测分析（7.1.10）：检测项完整性、汇总自洽、接口鉴别覆盖与 OpenAPI 同源
- 剩余信息保护（7.1.8）：临时目录统计与按保留期清理

运行：python manage.py test apps.system
"""
import hashlib
import json
import os
import time
from datetime import timedelta
from pathlib import Path

from django.conf import settings
from django.test import TestCase

from apps.project.models import Abbreviation, Project
from apps.system.models import BackupRecord
from apps.system.tools.backup import (BACKUP_MODELS, backup_dir, collect_rows, create_backup,
                                      delete_backup, restore_backup, verify_backup)
from apps.system.tools.residue import purge_temp_files, temp_dir_usage
from apps.system.tools.security_check import (CATEGORY_ORDER, CHECKS, IMPROVEMENTS, PASS, RISK,
                                              run_security_check)


class SecurityCheckTests(TestCase):
    """7.1.10 安全性检测分析"""

    def setUp(self):
        self.result = run_security_check()

    def test_all_checks_executed(self):
        """每个注册的检测项都应产出结论（单项异常也会降级为提示，不丢项）"""
        self.assertEqual(len(self.result['items']), len(CHECKS))

    def test_summary_is_consistent(self):
        summary = self.result['summary']
        items = self.result['items']
        self.assertEqual(summary['total'], len(items))
        self.assertEqual(summary['passed'] + summary['risk'] + summary['notice'] + summary['na'], len(items))

    def test_items_cover_five_categories(self):
        """五类被测对象都要有检测项，顺序与国标一致"""
        names = [c['name'] for c in self.result['summary']['categories']]
        self.assertEqual(names, CATEGORY_ORDER)

    def test_item_shape(self):
        for item in self.result['items']:
            for key in ('category', 'name', 'method', 'status', 'status_label', 'detail'):
                self.assertIn(key, item)
            # 风险项必须给出整改建议，否则检测没有落脚点
            if item['status'] == RISK:
                self.assertTrue(item['advice'], f'{item["name"]} 缺少整改建议')
            # 不适用项必须写明由谁承担
            if item['status'] == 'na':
                self.assertTrue(item['advice'], f'{item["name"]} 未标明承担方')

    def test_api_auth_coverage_matches_openapi(self):
        """接口鉴别覆盖率取自 OpenAPI 定义，与实时统计一致"""
        from cdtestplant_v1.api import api
        schema = api.get_openapi_schema()
        total = authed = 0
        for ops in schema.get('paths', {}).values():
            for method, op in ops.items():
                if method not in ('get', 'post', 'put', 'delete', 'patch'):
                    continue
                total += 1
                authed += 1 if op.get('security') else 0
        item = next(i for i in self.result['items'] if i['name'] == '接口鉴别覆盖率')
        self.assertIn(f'{total} 个接口中 {authed} 个要求鉴别', item['detail'])
        # 公开入口只允许登录、验证码、令牌刷新、一次性下载令牌
        self.assertLessEqual(total - authed, 4)

    def test_improvements_recorded(self):
        """检测→改进闭环要有记录，且每条都有发现与措施"""
        self.assertGreaterEqual(len(self.result['improvements']), 3)
        for imp in self.result['improvements']:
            self.assertTrue(imp['finding'])
            self.assertTrue(imp['action'])
        self.assertEqual(IMPROVEMENTS, self.result['improvements'])


class BackupTests(TestCase):
    """7.1.9 备份与故障恢复"""

    def setUp(self):
        self.created = []

    def tearDown(self):
        for record in self.created:
            path = backup_dir() / record.file_name
            BackupRecord.objects.filter(id=record.id).delete()
            if path.is_file():
                path.unlink()

    def _create(self, **kwargs):
        record, _ = create_backup(creator=None, **kwargs)
        self.created.append(record)
        return record

    def test_full_scope_covers_every_table(self):
        data = collect_rows()
        self.assertEqual(set(data), {f'{m._meta.app_label}.{m.__name__}' for m in BACKUP_MODELS})
        self.assertEqual(len(data['project.Project']), Project.objects.count())

    def test_project_scope_is_subset(self):
        """按项目备份应只带走该项目的数据，且确实比全量少"""
        from apps.project.models import Round
        mine = Project.objects.create(ident='RTEST1', name='单测项目甲', duty_person='单测负责人')
        other = Project.objects.create(ident='RTEST2', name='单测项目乙', duty_person='单测负责人')
        round_kwargs = {'key': '0', 'title': '第1轮测试', 'location': '单测'}
        Round.objects.create(ident='1', project=mine, **round_kwargs)
        Round.objects.create(ident='1', project=other, **round_kwargs)
        try:
            full = collect_rows()
            scoped = collect_rows(project_id=mine.id)
            self.assertEqual([r['id'] for r in scoped['project.Project']], [mine.id])
            # 子表按外键带入，且只带本项目那一份
            self.assertEqual([r['project_id'] for r in scoped['project.Round']], [mine.id])
            self.assertLess(sum(len(v) for v in scoped.values()), sum(len(v) for v in full.values()))
        finally:
            Round.objects.filter(project__in=[mine, other]).delete()
            Project.objects.filter(id__in=[mine.id, other.id]).delete()

    def test_incremental_scope_shrinks(self):
        """
        增量：水位线设为将来时间时，带时间字段的表应当采不到记录；
        没有时间字段的纯关系子表按设计整表带上（宁可多备不可漏备）。
        """
        future = timezone_now() + timedelta(days=30)
        data = collect_rows(since=future)
        for model in BACKUP_MODELS:
            label = f'{model._meta.app_label}.{model.__name__}'
            names = {f.name for f in model._meta.fields}
            if {'update_datetime', 'create_datetime'} & names:
                self.assertEqual(data[label], [], f'{model.__name__} 在水位线之后仍有数据')
            else:
                self.assertIsInstance(data[label], list)

    def test_create_and_verify(self):
        record = self._create(kind='full', project_id=None, name='单测备份')
        path = backup_dir() / record.file_name
        self.assertTrue(path.is_file())
        self.assertEqual(record.size_bytes, path.stat().st_size)
        self.assertEqual(record.digest, hashlib.sha256(path.read_bytes()).hexdigest())
        self.assertGreater(record.record_count, 0)
        self.assertTrue(verify_backup(record))

    def test_tampered_backup_is_detected(self):
        record = self._create(kind='full', project_id=None, name='单测备份-防篡改')
        path = backup_dir() / record.file_name
        payload = json.loads(path.read_text(encoding='utf-8'))
        payload['data']['project.Abbreviation'] = [{'title': '被改', 'des': '被改'}]
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding='utf-8')
        self.assertFalse(verify_backup(record))

    def test_restore_upserts_rows(self):
        """按主键 upsert：不存在的行新建，已存在的行更新"""
        record = self._create(kind='full', project_id=None, name='单测备份-恢复')
        path = backup_dir() / record.file_name
        payload = json.loads(path.read_text(encoding='utf-8'))

        abbr = Abbreviation.objects.create(title='单测缩略语', des='原值')
        # 补一条新行（不带主键 -> 新建）与一条改过的行（带主键 -> 更新）
        payload['data']['project.Abbreviation'] = [
            {'title': '单测缩略语-新建', 'des': '新建'},
            {'id': abbr.id, 'title': '单测缩略语', 'des': '更新后'},
        ]
        path.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True), encoding='utf-8')
        # 重算摘要，模拟一份"内容与摘要一致"的备份
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        BackupRecord.objects.filter(id=record.id).update(digest=digest)
        record.refresh_from_db()
        self.assertTrue(verify_backup(record))

        try:
            stats = restore_backup(record)
            self.assertEqual(stats['failed'], 0)
            self.assertGreaterEqual(stats['created'], 1)
            self.assertGreaterEqual(stats['updated'], 1)
            abbr.refresh_from_db()
            self.assertEqual(abbr.des, '更新后')
            self.assertTrue(Abbreviation.objects.filter(title='单测缩略语-新建').exists())
        finally:
            Abbreviation.objects.filter(title__startswith='单测缩略语').delete()

    def test_delete_removes_file(self):
        record = self._create(kind='full', project_id=None, name='单测备份-删除')
        path = backup_dir() / record.file_name
        self.assertTrue(path.is_file())
        delete_backup(record)
        self.created.remove(record)
        self.assertFalse(path.exists())
        self.assertFalse(BackupRecord.objects.filter(id=record.id).exists())


class ResidueTests(TestCase):
    """7.1.8 剩余信息保护"""

    def setUp(self):
        # 造一个符合清理规则的临时目录：media/<x>/temp/
        self.root = Path(settings.BASE_DIR) / 'media' / '__unit_test__' / 'temp'
        self.root.mkdir(parents=True, exist_ok=True)
        self.old_file = self.root / 'old_temp.tmp'
        self.old_file.write_text('x' * 100, encoding='utf-8')
        # 把 mtime 拨到 3 天前
        old = time.time() - 3 * 86400
        os.utime(self.old_file, (old, old))

    def tearDown(self):
        import shutil
        shutil.rmtree(Path(settings.BASE_DIR) / 'media' / '__unit_test__', ignore_errors=True)

    def test_usage_counts_temp_files(self):
        usage = temp_dir_usage()
        self.assertGreaterEqual(usage['file_count'], 1)
        self.assertGreaterEqual(usage['total_bytes'], 100)

    def test_purge_by_retention(self):
        """保留 24 小时时，3 天前的文件应被清掉"""
        result = purge_temp_files(max_age_hours=24)
        self.assertGreaterEqual(result['removed'], 1)
        self.assertGreaterEqual(result['freed_bytes'], 100)
        self.assertFalse(self.old_file.exists())

    def test_purge_keeps_fresh_files(self):
        result = purge_temp_files(max_age_hours=24 * 365)
        self.assertEqual(result['removed'], 0)
        self.assertTrue(self.old_file.exists())


def timezone_now():
    from django.utils import timezone
    return timezone.now()
