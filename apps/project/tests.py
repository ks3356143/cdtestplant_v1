# -*- coding: utf-8 -*-
"""
apps/project 单元测试 —— 数据完整性标签（GB/T 28452-2012 第三级 7.1.7）

覆盖：
- 写操作后自动刷新标签（重要数据 Project / 一般数据 Round）
- 绕过应用直改数据库后的使用前检测（verify_instance / ensure_intact）
- 批量更新路径的标签补刷（refresh_tags）
- 报告生成前的整轮校验（verify_round / ensure_round_intact）
- 历史数据缺标签时的基准补建

运行：python manage.py test apps.project
"""
from django.test import TestCase
from ninja.errors import HttpError

from apps.project.models import Project, Round
from apps.project.tools.integrity import (compute_digest, ensure_intact, ensure_round_intact,
                                          refresh_tags, verify_instance, verify_round)
from apps.system.models import AuditLog, DataIntegrityTag


def make_project(**kwargs):
    defaults = dict(ident='T-ITG-1', name='完整性单元测试项目', duty_person='张三',
                    quality_person='李四', vise_person='王五', config_person='赵六',
                    entrust_unit='委托单位', dev_unit='研制单位', test_unit='测评单位')
    defaults.update(kwargs)
    return Project.objects.create(**defaults)


class IntegrityTagTests(TestCase):
    """7.1.7 b/e：存储完整性标签与使用前检测"""

    def setUp(self):
        self.project = make_project()
        self.round = Round.objects.create(project=self.project, ident='R1', name='第一轮',
                                          key='0', title='第1轮', location='测评中心')

    def _tag(self, instance):
        return DataIntegrityTag.objects.filter(
            table_name=instance._meta.db_table, object_id=str(instance.pk)).first()

    def test_tag_created_after_save(self):
        """重要数据与一般数据在保存后都应自动产生 SHA256 标签"""
        self.assertIsNotNone(self._tag(self.project))
        self.assertIsNotNone(self._tag(self.round))
        self.assertEqual(self._tag(self.project).algorithm, 'SHA256')

    def test_digest_changes_with_protected_field(self):
        """参与摘要的关键字段变化时摘要必须变化"""
        before = compute_digest(self.project, ['ident', 'name', 'secret'])
        self.project.name = '改名后的项目'
        after = compute_digest(self.project, ['ident', 'name', 'secret'])
        self.assertNotEqual(before, after)

    def test_verify_intact_after_normal_save(self):
        result = verify_instance(self.project)
        self.assertTrue(result['intact'])
        self.assertFalse(result['backfilled'])

    def test_verify_detects_raw_database_tamper(self):
        """绕过 ORM 的应用层写路径（queryset.update）不会刷新标签，使用前校验应发现"""
        Project.objects.filter(pk=self.project.pk).update(name='被直接篡改的名称')
        self.project.refresh_from_db()
        result = verify_instance(self.project)
        self.assertFalse(result['intact'])
        self.assertNotEqual(result['stored'], result['actual'])

    def test_ensure_intact_raises_409_with_alert_payload(self):
        """破损时拒绝继续使用，告警文案挂在异常上交给接口层落库（避免事务回滚丢失）"""
        Project.objects.filter(pk=self.project.pk).update(secret='5')
        self.project.refresh_from_db()
        before = AuditLog.objects.filter(event_type='integrity_broken').count()
        with self.assertRaises(HttpError) as ctx:
            ensure_intact(self.project, action='读取用例')
        self.assertEqual(ctx.exception.status_code, 409)
        self.assertIn('读取用例前完整性校验失败', ctx.exception.integrity_event)
        # 直接调用没有接口异常处理器，因此此处不落库；落库行为由 API 测试覆盖
        self.assertEqual(AuditLog.objects.filter(event_type='integrity_broken').count(), before)

    def test_refresh_tags_repairs_bulk_update_drift(self):
        """bulk_update/queryset.update 后统一补刷标签，校验应恢复完好"""
        Round.objects.filter(pk=self.round.pk).update(name='批量修改后的轮次')
        self.round.refresh_from_db()
        self.assertFalse(verify_instance(self.round)['intact'])
        changed = refresh_tags([self.round])
        self.assertEqual(changed, 1)
        self.assertTrue(verify_instance(self.round)['intact'])

    def test_verify_round_detects_broken_child(self):
        """生成报告前的整轮校验能定位到具体破损记录（含一般数据）"""
        Round.objects.filter(pk=self.round.pk).update(location='被篡改的地点')
        self.round.refresh_from_db()
        broken = verify_round(self.project, '0')
        self.assertEqual(len(broken), 1)
        self.assertEqual(broken[0]['table'], 'project_round')
        self.assertEqual(broken[0]['id'], self.round.pk)

    def test_ensure_round_intact_blocks_report_generation(self):
        Round.objects.filter(pk=self.round.pk).update(grade='9')
        with self.assertRaises(HttpError) as ctx:
            ensure_round_intact(self.project, '0', action='生成测评报告')
        self.assertEqual(ctx.exception.status_code, 409)
        self.assertIn('生成测评报告前数据完整性校验失败', ctx.exception.message)

    def test_verify_round_passes_when_clean(self):
        self.assertEqual(verify_round(self.project, '0'), [])
        self.assertTrue(ensure_round_intact(self.project, '0'))

    def test_missing_tag_is_backfilled_on_first_use(self):
        """历史数据尚无标签时先补建基准并视为完好"""
        DataIntegrityTag.objects.filter(
            table_name=self.round._meta.db_table, object_id=str(self.round.pk)).delete()
        result = verify_instance(self.round)
        self.assertTrue(result['intact'])
        self.assertTrue(result['backfilled'])
        self.assertIsNotNone(self._tag(self.round))


class BatchImportApiTests(TestCase):
    """批量导入接口的错误码统一：解析错误一律 HTTP 400，成功统一 code=200"""

    def setUp(self):
        from ninja_jwt.tokens import RefreshToken
        from apps.user.models import Users
        self.user = Users.objects.create_user(username='t_batch_admin', password='x',
                                              name='批量测试管理员', role='admin')
        self.token = str(RefreshToken.for_user(self.user).access_token)
        self.project = make_project(ident='T-BATCH-1', name='批量导入测试项目')
        self.round = Round.objects.create(project=self.project, ident='R1', name='第一轮',
                                          key='0', title='第1轮', location='测评中心')

    def _post(self, path, payload):
        import json
        response = self.client.post(path, data=json.dumps(payload),
                                    content_type='application/json',
                                    HTTP_AUTHORIZATION=f'Bearer {self.token}')
        return response.status_code, json.loads(response.content)

    def test_demand_batch_parse_error_returns_400(self):
        status, body = self._post('/api/project/testDemand/multi_save', {
            'project_id': self.project.id,
            'demands': [{'parent_key': '0-0-0', 'ident': 'T1', 'name': '测试项',
                         'priority': '1', 'adequacy': '充分', 'testContent': '^@没有名称',
                         'testMethod': [], 'testType': 'FT', 'testDesciption': ''}],
        })
        self.assertEqual(status, 400)
        self.assertIn('没有测试子项名称', body['message'])
        self.assertFalse(body['success'])

    def test_case_batch_parse_error_returns_400(self):
        status, body = self._post('/api/project/case/multi_save', {
            'project_id': self.project.id,
            'cases': [{'parent_key': '0-0-0-0', 'name': '用例', 'test_step': '没有分隔符的一行'}],
        })
        self.assertEqual(status, 400)
        self.assertIn('@', body['message'])

    def test_case_batch_missing_parent_returns_400(self):
        status, body = self._post('/api/project/case/multi_save', {
            'project_id': self.project.id,
            'cases': [{'parent_key': 'not-exist', 'name': '用例', 'test_step': '操作@预期'}],
        })
        self.assertEqual(status, 400)
        self.assertIn('测试项不存在', body['message'])

    def _create_chain(self):
        """建 轮次→被测件→设计需求 三层树节点（批量导入的父级）"""
        from apps.project.models import Design, Dut
        dut = Dut.objects.create(project=self.project, round=self.round, ident='D1',
                                 name='被测件', key='0-0', title='被测件')
        return Design.objects.create(project=self.project, round=self.round, dut=dut,
                                     ident='DS1', name='设计需求', key='0-0-0', title='设计需求')

    def test_demand_batch_success_uses_standard_code(self):
        from apps.project.models import TestDemand
        self._create_chain()
        status, body = self._post('/api/project/testDemand/multi_save', {
            'project_id': self.project.id,
            'demands': [{'parent_key': '0-0-0', 'ident': 'T1', 'name': '测试项',
                         'priority': '1', 'adequacy': '充分',
                         'testContent': '^子项@描述\n操作@预期',
                         'testMethod': [], 'testType': 'FT', 'testDesciption': ''}],
        })
        self.assertEqual(status, 200)
        self.assertEqual(body['code'], 200)
        self.assertTrue(body['success'])
        self.assertEqual(body['data'], ['0-0-0-0'])
        self.assertTrue(TestDemand.objects.filter(project=self.project, ident='T1').exists())

    def test_case_batch_success_uses_standard_code(self):
        from apps.project.models import Case
        self._create_chain()
        _, demand_body = self._post('/api/project/testDemand/multi_save', {
            'project_id': self.project.id,
            'demands': [{'parent_key': '0-0-0', 'ident': 'T2', 'name': '测试项',
                         'priority': '1', 'adequacy': '充分', 'testContent': '',
                         'testMethod': [], 'testType': 'FT', 'testDesciption': ''}],
        })
        parent_key = demand_body['data'][0]
        status, body = self._post('/api/project/case/multi_save', {
            'project_id': self.project.id,
            'cases': [{'parent_key': parent_key, 'name': '用例一', 'test_step': '操作@预期'}],
        })
        self.assertEqual(status, 200)
        self.assertEqual(body['code'], 200)
        self.assertTrue(body['success'])
        self.assertEqual(body['data'], [parent_key + '-0'])
        self.assertTrue(Case.objects.filter(project=self.project, name='用例一').exists())


class IntegrityUseBeforeApiTests(TestCase):
    """7.1.7 b/e：读取用例前的完整性校验必须真正留下篡改告警（不能被事务回滚）"""

    def setUp(self):
        from ninja_jwt.tokens import RefreshToken
        from apps.user.models import Users
        from apps.project.models import Case, Design, Dut, TestDemand
        self.user = Users.objects.create_user(username='t_integrity_admin', password='x',
                                              name='完整性接口测试', role='admin')
        self.token = str(RefreshToken.for_user(self.user).access_token)
        self.project = make_project(ident='T-INT-API-1', name='完整性接口测试项目')
        self.round = Round.objects.create(project=self.project, ident='R1', name='第一轮',
                                          key='0', title='第1轮', location='测评中心')
        self.dut = Dut.objects.create(project=self.project, round=self.round, ident='D1',
                                      name='被测件', key='0-0', title='被测件')
        self.design = Design.objects.create(project=self.project, round=self.round, dut=self.dut,
                                            ident='DS1', name='设计需求', key='0-0-0', title='设计需求')
        self.demand = TestDemand.objects.create(project=self.project, round=self.round, dut=self.dut,
                                                design=self.design, ident='T1', name='测试项',
                                                key='0-0-0-0', title='测试项')
        self.case = Case.objects.create(project=self.project, round=self.round, dut=self.dut,
                                        design=self.design, test=self.demand, ident='C1',
                                        name='原始用例', key='0-0-0-0-0', title='原始用例')

    def _get_case(self):
        return self.client.get('/api/project/getCaseOne', {'key': self.case.key,
                                                           'projectId': self.project.id},
                               HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_tampered_case_read_alert_is_persisted(self):
        """直改用例后读取：409 且 integrity_broken 告警未被视图事务回滚掉"""
        from apps.project.models import Case
        Case.objects.filter(pk=self.case.pk).update(name='被直接篡改')
        try:
            response = self._get_case()
            self.assertEqual(response.status_code, 409)
            alert = AuditLog.objects.filter(event_type='integrity_broken').order_by('-id').first()
            self.assertIsNotNone(alert)
            self.assertFalse(alert.success)
            self.assertIn('读取用例前完整性校验失败', alert.detail)
        finally:
            Case.objects.filter(pk=self.case.pk).update(name='原始用例')
            refresh_tags([Case.objects.get(pk=self.case.pk)])

    def test_restored_case_read_succeeds(self):
        from apps.project.models import Case
        Case.objects.filter(pk=self.case.pk).update(name='被直接篡改')
        Case.objects.filter(pk=self.case.pk).update(name='原始用例')
        refresh_tags([Case.objects.get(pk=self.case.pk)])
        response = self._get_case()
        self.assertEqual(response.status_code, 200)
