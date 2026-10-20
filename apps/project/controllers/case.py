from ninja_extra import api_controller, ControllerBase, route
from ninja import Query
from ninja_jwt.authentication import JWTAuth
from ninja_extra.permissions import IsAuthenticated
from ninja.pagination import paginate
from ninja.errors import HttpError
from utils.chen_pagination import MyPagination
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.db.models.functions import Replace
from django.db.models import F, Value
from typing import List
from faker import Faker
from datetime import datetime
from django.utils import timezone
from utils.chen_response import ChenResponse
from utils.chen_crud import multi_delete_case
from apps.project.models import Design, Dut, Round, TestDemand, Case, CaseStep, Project, Problem, NonrepudiationEvidence, \
    TestDemandContentStep
from apps.project.tools.access_control import (check_project_access, check_project_access_by_id,
                                               check_objects_access, get_object_in_project)
from apps.project.schemas.case import DeleteSchema, CaseModelOutSchema, CaseFilterSchema, \
    CaseTreeReturnSchema, ReplaceCaseSchema, PersonReplaceSchema, ExetimeReplaceSchema, \
    CaseTreeInputSchema, CaseCreateOutSchema, CaseCreateInputSchema, DemandNodeSchema, \
    CaseModelOutSchemaWithoutProblem, BatchCreateCaseInputSchema
from utils.util import get_testType
from utils.codes import HTTP_INDEX_ERROR, HTTP_EXISTS_CASES
from apps.project.tools.copyCase import case_move_to_test, case_copy_to_test, case_to_case_copy_or_move
from utils.smallTools.interfaceTools import conditionNoneToBlank
from apps.project.tool.batchTools import parse_case_content_string

# 批量替换允许的文本字段白名单：防止前端传入任意字段名导致 ORM 异常或越权改写
CASE_REPLACE_FIELDS = {
    'ident', 'name', 'title', 'initialization', 'premise', 'summarize',
    'designPerson', 'testPerson', 'monitorPerson',
}


def _step_to_values(step: CaseStep) -> dict:
    """CaseStep 实例转 dict，键与原 queryset.values() 保持一致（供预取后手工序列化）"""
    return {
        'id': step.id,
        'operation': step.operation,
        'expect': step.expect,
        'result': step.result,
        'passed': step.passed,
        'case_id': step.case_id,
        'remark': step.remark,
        'update_datetime': step.update_datetime,
        'create_datetime': step.create_datetime,
        'sort': step.sort,
    }


def _content_step_to_values(step: TestDemandContentStep) -> dict:
    """TestDemandContentStep 实例转 dict，键与 .values() 保持一致"""
    return {
        'id': step.id,
        'operation': step.operation,
        'expect': step.expect,
        'testDemandContent_id': step.testDemandContent_id,
        'remark': step.remark,
        'update_datetime': step.update_datetime,
        'create_datetime': step.create_datetime,
        'sort': step.sort,
    }


@api_controller("/project", auth=JWTAuth(), permissions=[IsAuthenticated], tags=['测试用例接口'])
class CaseController(ControllerBase):
    @route.get("/getCaseList", response=List[CaseModelOutSchema], exclude_none=True,
               url_name="case-list")
    @transaction.atomic
    @paginate(MyPagination)
    def get_case_list(self, data: CaseFilterSchema = Query(...)):
        """有id则查询一个case，无id则查询多个"""
        data_dict = data.dict()
        case_id = data_dict.pop('id')
        check_project_access_by_id(data.project_id, self.context.request.user)
        if case_id:
            # 当传入了id，则查询单个
            qs = Case.objects.filter(id=case_id).select_related('test').prefetch_related(
                'caseField', 'step', 'test__testQField__testStepField')  # type:ignore
        else:
            conditionNoneToBlank(data)
            query_params = {
                'project__id': data.project_id,
                'ident__icontains': data.ident,
                'name__icontains': data.name,
                'designPerson__icontains': data.designPerson,
                'testPerson__icontains': data.testPerson,
                'monitorPerson__icontains': data.monitorPerson,
                'summarize__icontains': data.summarize
            }
            # 如果没有多个key则是“那个汇总界面”
            if data.dut_id and data.design_id and data.test_id:
                test_key = "".join([data.round_id, '-', data.dut_id, '-', data.design_id, '-', data.test_id])
                query_params['test__key'] = test_key
            else:
                # 汇总界面只查round
                query_params['round__key'] = data.round_id
            qs = (Case.objects.filter(**query_params).order_by("key").select_related('test')
                  .prefetch_related('caseField', 'step', 'test__testQField__testStepField'))
        # 由于有嵌套query_set存在，把每个用例的schema加上一个字段（步骤已在预取中取回，不再逐用例查库）
        query_list = []
        for query_single in qs:
            setattr(query_single, "testStep", [_step_to_values(s) for s in query_single.step.all()])
            # 增加一个字段，测试类型例如：FT
            setattr(query_single, 'testType', get_testType(query_single.test.testType, dict_code='testType'))
            # 如果有问题单字段则添加上
            related_problem: Problem = query_single.caseField.first()
            if related_problem:
                setattr(query_single, 'problem', related_problem)
            # 2025年5月10日在test字段加上testContent
            test_obj = query_single.test
            sub_list = []
            for step_obj in test_obj.testQField.all():
                setattr(step_obj, "subStep", [_content_step_to_values(s) for s in step_obj.testStepField.all()])
                sub_list.append(step_obj)
            setattr(test_obj, "testContent", sub_list)
            setattr(query_single, 'test', test_obj)
            query_list.append(query_single)
        return query_list

    @route.get("/getCaseOne", response=CaseModelOutSchemaWithoutProblem, url_name='case-one')
    @transaction.atomic
    def get_case_one(self, key: str, projectId: int):
        check_project_access_by_id(projectId, self.context.request.user)
        """用于在用例树状页面，获取promblem信息，这里根据key获取信息"""
        project_obj = get_object_or_404(Project, id=projectId)
        case = project_obj.pcField.filter(key=key).first()
        if case:
            setattr(case, "testStep", case.step.all().values())
            setattr(case, 'testType', get_testType(case.test.testType, dict_code='testType'))
            return case
        raise HttpError(404, "您获取的数据不存在")

    @route.get("/getCaseOneById", response=CaseModelOutSchemaWithoutProblem, url_name='case-one-by-id')
    @transaction.atomic
    def get_case_by_id(self, id: int):
        """用于在用例树状页面，获取promblem信息，这里根据key获取信息"""
        case = Case.objects.filter(id=id).first()
        if case:
            check_project_access(case.project, self.context.request.user)
            setattr(case, "testStep", case.step.all().values())
            setattr(case, 'testType', get_testType(case.test.testType, dict_code='testType'))
            return case
        raise HttpError(404, "您获取的数据不存在")

    # 处理树状数据
    @route.get("/getCaseInfo", response=List[CaseTreeReturnSchema], url_name="case-info")
    @transaction.atomic
    def get_case_tree(self, payload: CaseTreeInputSchema = Query(...)):
        check_project_access_by_id(payload.project_id, self.context.request.user)
        qs = Case.objects.filter(project__id=payload.project_id, test__key=payload.key) \
            .prefetch_related('caseField', 'step')  # type:ignore
        for q in qs:
            # 遍历每个用例节点，查看是否有关联问题单
            if q.caseField.all():
                q.isRelatedProblem = True
            # 遍历用例的step查看是否有未通过
            q.isNotPassed = any(step.passed == '2' for step in q.step.all())
        return qs

    # 添加测试用例
    @route.post("/case/save", response=CaseCreateOutSchema, url_name="case-create")
    @transaction.atomic
    def create_case(self, payload: CaseCreateInputSchema):
        check_project_access_by_id(payload.project_id, self.context.request.user)
        asert_dict = payload.dict(exclude_none=True)
        # 构造demand_key
        test_whole_key = "".join(
            [payload.round_key, "-", payload.dut_key, '-', payload.design_key, '-', payload.test_key])
        # 查询当前key应该为多少
        case_count = Case.objects.filter(project__id=payload.project_id,  # type:ignore
                                         test__key=test_whole_key).count()
        key_string = ''.join([test_whole_key, "-", str(case_count)])
        # 查询当前各个前面节点的instance
        round_instance = Round.objects.get(project__id=payload.project_id, key=payload.round_key)
        dut_instance = Dut.objects.get(project__id=payload.project_id,  # type:ignore
                                       key="".join([payload.round_key, "-", payload.dut_key]))
        design_instance = Design.objects.get(project__id=payload.project_id, key="".join(  # type:ignore
            [payload.round_key, "-", payload.dut_key, '-', payload.design_key]))
        test_instance = TestDemand.objects.get(project__id=payload.project_id, key="".join(  # type:ignore
            [payload.round_key, "-", payload.dut_key, '-', payload.design_key, '-', payload.test_key]))
        # 直接把测试项的标识给前端处理显示
        asert_dict['ident'] = test_instance.ident
        # ~~~~~~~~~end~~~~~~~~~
        asert_dict.update(
            {'key': key_string, 'round': round_instance, 'dut': dut_instance, 'design': design_instance,
             "test": test_instance, 'title': payload.name})
        asert_dict.pop("round_key")
        asert_dict.pop("dut_key")
        asert_dict.pop("design_key")
        asert_dict.pop("test_key")
        asert_dict.pop("testStep")
        qs = Case.objects.create(**asert_dict)  # type:ignore
        # 对testStep单独处理
        data_list = []
        for item in payload.dict()["testStep"]:
            if not isinstance(item, dict):
                item = item.dict()
            item["case"] = qs
            data_list.append(CaseStep(**item))
        CaseStep.objects.bulk_create(data_list)  # type:ignore
        if data_list:
            from apps.project.tools.integrity import refresh_tags
            refresh_tags(list(qs.step.all()))
        return qs

    # 批量新增用例
    @route.post("/case/multi_save", url_name="case-batch-create")
    @transaction.atomic
    def multi_case_save(self, payload: BatchCreateCaseInputSchema):
        check_project_access_by_id(payload.project_id, self.context.request.user)
        project_obj = get_object_or_404(Project, id=payload.project_id)
        user_name = self.context.request.user.name
        keys = []
        created_cases = []
        demands = project_obj.ptField.all()  # 当前项目所有测试项
        for case_data in payload.cases:
            # 解析放在前面防止出错
            stepsOrErrorResponse = parse_case_content_string(case_data.test_step)
            if isinstance(stepsOrErrorResponse, ChenResponse):
                return stepsOrErrorResponse
            # 查询当前测试项下case数量，以设置case的key
            demand_key = case_data.parent_key
            demand_obj = demands.filter(key=demand_key).first()
            if not demand_obj:
                return ChenResponse(status=400, code=60004, message=f'测试项不存在：{demand_key}，请检查')
            case_count = demand_obj.tcField.count()
            key_string = ''.join([demand_key, "-", str(case_count)])
            keys.append(key_string)
            case_dict = {
                "ident": demand_obj.ident,
                "name": case_data.name,
                "key": key_string,
                "initialization": case_data.initialization,
                "premise": case_data.premise,
                "summarize": case_data.summarize,
                "designPerson": user_name,
                "testPerson": user_name,
                "monitorPerson": user_name,
                "project": project_obj,
                "round": demand_obj.round,
                "dut": demand_obj.dut,
                "design": demand_obj.design,
                "test": demand_obj,
                "exe_time": timezone.now(),
                "timing_diagram": case_data.sequence,
                "title": case_data.name
            }
            case_new_obj = Case.objects.create(**case_dict)
            created_cases.append(case_new_obj)
            case_step_list = []
            for step in stepsOrErrorResponse:
                case_step_list.append(CaseStep(**{"case": case_new_obj, "operation": step['operation'],
                                                  "expect": step['expect']}))
            if case_step_list:
                CaseStep.objects.bulk_create(case_step_list)
        # bulk_create 不触发 post_save，统一补刷新建用例步骤的完整性标签
        if created_cases:
            from apps.project.tools.integrity import refresh_tags
            refresh_tags(list(CaseStep.objects.filter(case__in=created_cases)))
        return ChenResponse(code=60000, status=200, data=keys, message='成功录入用例')

    # 更新测试用例
    @route.put("/case/update/{id}", response=CaseCreateOutSchema, url_name="case-update")
    @transaction.atomic
    def update_case(self, id: int, payload: CaseCreateInputSchema):
        # 目标用例必须属于 payload 指定的项目，防止拿 A 项目权限改 B 项目数据
        case_qs = get_object_in_project(Case, id, payload.project_id, self.context.request.user)
        for attr, value in payload.dict().items():
            if attr == 'project_id' or attr == 'round_key' or attr == 'dut_key' or attr == 'design_key' or attr == 'test_key':
                continue
            if attr == 'name':
                setattr(case_qs, "title", value)
            # testStep处理
            if attr == 'testStep':
                # 旧的步骤整体删除后重建（批量删除/批量创建，避免逐条往返）
                case_qs.step.all().delete()
                data_list = []
                for item in value:
                    # 前端可能提交整表空白行，跳过没有任何内容的步骤
                    has_content = bool(item.get('operation') or item.get('expect') or item.get('result'))
                    if not has_content and item.get('passed') in (None, '', '3'):
                        continue
                    data_list.append(CaseStep(
                        case=case_qs,
                        operation=item.get('operation'),
                        expect=item.get('expect'),
                        result=item.get('result'),
                        passed=item.get('passed') or '3',
                    ))
                if data_list:
                    CaseStep.objects.bulk_create(data_list)  # type:ignore
                    # bulk_create 不触发 post_save，显式补刷完整性标签
                    from apps.project.tools.integrity import refresh_tags
                    refresh_tags(list(case_qs.step.all()))
                continue

            setattr(case_qs, attr, value)
        # 处理标识-统一设置为YL
        case_qs.ident = case_qs.test.ident
        # ~~~~~~~~~end~~~~~~~~~
        case_qs.save()
        # 抗抵赖证据：用例执行结果提交 → 原发证据（测试人员身份+时间戳+步骤结果摘要，GB/T 28452 7.1.2）
        executed_steps = [item for item in (payload.dict().get('testStep') or []) if item.get('result')]
        if executed_steps:
            NonrepudiationEvidence.record(
                request=self.context.request, evidence_type='1', actor=self.context.request.user,
                action='用例执行结果提交', business_type='case', business_ident=str(case_qs.id),
                business_name=case_qs.name,
                payload={'case_ident': case_qs.ident, 'case_name': case_qs.name,
                         'steps': [{'operation': s.get('operation'), 'result': s.get('result'),
                                    'passed': s.get('passed')} for s in executed_steps]},
            )
        return case_qs

    # 删除测试用例
    @route.delete("/case/delete", url_name="case-delete")
    @transaction.atomic
    def delete_case(self, data: DeleteSchema):
        # 逐个校验每条选中用例的项目归属（防止只校验第一行、其余行跨项目删除）
        case_objs = check_objects_access(Case, data.ids, self.context.request.user)
        affected = {(obj.test_id, obj.test.key) for obj in case_objs}
        multi_delete_case([obj.id for obj in case_objs], Case)
        # 每个受影响的测试项都重排 key（批量删除可能跨多个测试项）
        for test_id, test_key in affected:
            case_all = list(Case.objects.filter(test__id=test_id).order_by('id'))  # type:ignore
            for index, single_qs in enumerate(case_all):
                single_qs.key = "".join([test_key, '-', str(index)])
            if case_all:
                Case.objects.bulk_update(case_all, ['key'])
        return ChenResponse(message="测试用例删除成功！影响域分析中如果有该关联用例则被删除。")

    # 右键测试项，根据测试子项生成用例
    @route.post("/case/create_by_demand", url_name='case-create-by-demand')
    @transaction.atomic
    def create_case_by_demand(self, demand_node: DemandNodeSchema):
        check_project_access_by_id(demand_node.project_id, self.context.request.user)
        project_qs = get_object_or_404(Project, id=demand_node.project_id)
        created_cases = []
        if demand_node.key and demand_node.key != '':
            demand = get_object_or_404(TestDemand, key=demand_node.key, project=project_qs)
            # 先查询当前测试项下面有无case
            case_exists = demand.tcField.exists()
            if case_exists:
                return ChenResponse(status=500, code=HTTP_EXISTS_CASES,
                                    message='测试项下面有用例，请删除后生成')
            # 查询所有测试子项
            sub_items = demand.testQField.all()
            # 每一个子项都创建一个用例，先声明一个列表，后面可以bulk_create
            index = 0
            for sub in sub_items:
                user_name = self.context.request.user.name  # type:ignore
                case_dict = {
                    'ident': demand.ident,
                    'name': sub.subName,
                    'initialization': '软件正常启动，正常运行',
                    'premise': '软件正常启动，外部接口运行正常',
                    'summarize': demand.testDesciption,
                    'designPerson': user_name,
                    'testPerson': user_name,
                    'monitorPerson': user_name,
                    'project': project_qs,
                    'round': demand.round,
                    'dut': demand.dut,
                    'design': demand.design,
                    'test': demand,
                    'title': sub.subName,
                    'key': ''.join([demand_node.key, '-', str(index)]),
                    'level': '4',
                }
                case_model = Case.objects.create(**case_dict)  # type:ignore
                created_cases.append(case_model)
                # 创建用例步骤（批量写入）
                step_list = []
                for demand_step_obj in sub.testStepField.all():
                    operation = demand_step_obj.operation
                    step_list.append(CaseStep(
                        operation="".join([operation if operation is not None else ""]),
                        expect=demand_step_obj.expect,
                        result='',  # 暂时为空
                        case=case_model,  # 指定父级Case模型
                    ))
                if step_list:
                    CaseStep.objects.bulk_create(step_list)  # type:ignore
                index += 1
        # bulk_create 不触发 post_save，统一补刷新建用例步骤的完整性标签
        if created_cases:
            from apps.project.tools.integrity import refresh_tags
            refresh_tags(list(CaseStep.objects.filter(case__in=created_cases)))
        # 这里返回一个demand的key用于前端刷新树状图
        return ChenResponse(data={'key': demand_node.key}, status=200, code=200,
                            message='测试项自动生成用例成功')

    # 测试用例复制/移动到测试项上
    @route.get("/case/copy_or_move_to_demand", url_name='case-copy-move-demand')
    @transaction.atomic
    def copy_move_case_to_demand(self, project_id: int, case_key: str, demand_key: str, move: bool):
        check_project_access_by_id(project_id, self.context.request.user)
        if move:  # 移动
            old_key, new_key = case_move_to_test(project_id, case_key, demand_key)
        else:  # 复制
            old_key, new_key = case_copy_to_test(project_id, case_key, demand_key)
        # 返回刷新树状信息-需要刷新2个，原来的case_key和现在的case_key
        return ChenResponse(data={'oldCaseKey': {'key': old_key}, 'newCaseKey': {'key': new_key}})

    # 测试用例复制/移动到用例
    @route.get("/case/copy_or_move_by_case", url_name='case-copy-move-case')
    @transaction.atomic
    def copy_move_case_by_case(self, project_id: int, drag_key: str, drop_key: str, move: bool,
                               position: int):
        case_to_case_copy_or_move(project_id, drag_key, drop_key, move, position)
        return ChenResponse(data={'old': {'key': drag_key}, 'new': {'key': drop_key}})

    # 用例-替换接口
    @route.post("/case/replace/", url_name='case-replace')
    @transaction.atomic
    def replace_case_step_content(self, payload: ReplaceCaseSchema):
        check_project_access_by_id(payload.project_id, self.context.request.user)
        # 1.首先查询项目
        project_obj: Project = get_object_or_404(Project, id=payload.project_id)
        # 2.查询[所有轮次]的selectRows的id
        case_qs = project_obj.pcField.filter(id__in=payload.selectRows, round__key=payload.round_key)
        # 3.批量替换里面文本（解构不影响老数组）
        selectColumn = [x for x in payload.selectColumn if x != 'testStep']
        unknown = [x for x in selectColumn if x not in CASE_REPLACE_FIELDS]
        if unknown:
            return ChenResponse(status=400, code=400, message=f'不支持替换的字段：{unknown}')
        replace_kwargs = {
            field_name: Replace(F(field_name), Value(payload.originText), Value(payload.replaceText))
            for field_name in selectColumn
        }
        # 4.单独处理testContentStep的操作、预期-查询所有
        # 4.1.获取所有关联的TestDemandContentStep
        step_count = 0
        if 'testStep' in payload.selectColumn:
            caseStep_qs = CaseStep.objects.filter(case__in=case_qs)
            # 批量更新 operation 和 expect
            step_count = caseStep_qs.update(
                operation=Replace(F('operation'), Value(payload.originText), Value(payload.replaceText)),
                expect=Replace(F('expect'), Value(payload.originText), Value(payload.replaceText)),
                result=Replace(F('result'), Value(payload.originText), Value(payload.replaceText))
            )
        # 5.提交更新
        replace_count = case_qs.update(**replace_kwargs)
        return {'count': replace_count + step_count}

    # 批量替换设计人员、执行人员、审核人员
    @route.post("/case/personReplace/", url_name='case-person-replace')
    @transaction.atomic
    def bulk_replace_person(self, payload: PersonReplaceSchema):
        # 访问控制：对整批选中的用例逐一校验，避免只检查第一行造成跨项目篡改（自主访问控制 7.1.3）
        selected_case_qs = Case.objects.filter(id__in=payload.selectRows).select_related('project')
        for project in {c.project for c in selected_case_qs}:
            check_project_access(project, self.context.request.user)
        # 替换设计人员
        case_qs = selected_case_qs
        replace_count = 0
        if payload.designPerson != '不替换' and payload.designPerson != '':
            replace_count += case_qs.update(designPerson=payload.designPerson)
        if payload.testPerson != '不替换' and payload.testPerson != '':
            replace_count += case_qs.update(testPerson=payload.testPerson)
        if payload.monitorPerson != '不替换' and payload.monitorPerson != '':
            replace_count += case_qs.update(monitorPerson=payload.monitorPerson)
        return ChenResponse(message="批量替换成功", data={'count': replace_count})

    # 批量替换时间
    @route.post("/case/timeReplace/", url_name='case-time-replace')
    @transaction.atomic
    def bulk_replace_time(self, payload: ExetimeReplaceSchema):
        selected_case_ids = payload.selectRows
        if not selected_case_ids:
            return ChenResponse(status=500, code=50999, message='未选择行!', data="")
        # 访问控制：对整批选中的用例逐一校验，避免只检查第一行造成跨项目篡改（自主访问控制 7.1.3）
        selected_case_qs = Case.objects.filter(id__in=payload.selectRows).select_related('project')
        for project in {c.project for c in selected_case_qs}:
            check_project_access(project, self.context.request.user)
        # 随机日期
        start, end = payload.exetime
        start_date = datetime.strptime(start, "%Y-%m-%d").date()
        end_date = datetime.strptime(end, "%Y-%m-%d").date()
        # 更新的case的id列表
        updated_cases = []
        # 替换设计人员
        case_qs = selected_case_qs
        faker = Faker()
        # 逐个更新
        for case in case_qs:
            random_date = faker.date_between(start_date=start_date, end_date=end_date)
            formatted_date = random_date.strftime("%Y-%m-%d")
            case.exe_time = formatted_date
            updated_cases.append(case)
        Case.objects.bulk_update(updated_cases, ['exe_time'])
        return ChenResponse(status=200, code=200, data=len(updated_cases),
                            message=f"成功更新{len(updated_cases)}个用例执行时间")

    # 给级联选择器数据 -> 上一轮次所有用例
    @route.get("/case/getRelatedCase", url_name='case-related-case')
    def get_cases_related_case(self, id: int, round_key: str):
        check_project_access_by_id(id, self.context.request.user)
        project_obj = get_object_or_404(Project, id=id)
        previous_round_obj = project_obj.pField.filter(key=int(round_key) - 1).first()
        # 无上一轮次（首轮或上一轮已被删除）时返回空数据，避免崩溃
        if not previous_round_obj:
            return ChenResponse(message='获取成功', data=[])
        # dut -> design
        data_list = []
        for dut in previous_round_obj.rdField.all():
            dut_dict = {'label': dut.name, 'value': dut.id, 'key': dut.key, 'children': []}
            for design in dut.rsField.all():
                design_dict = {'label': design.name, 'value': design.id, 'key': design.key, 'children': []}
                for case in design.dcField.all():
                    case_dict = {'label': case.name, 'value': case.id, 'key': case.key}
                    design_dict['children'].append(case_dict)
                dut_dict['children'].append(design_dict)
            data_list.append(dut_dict)
        return ChenResponse(message='获取成功', data=data_list)
