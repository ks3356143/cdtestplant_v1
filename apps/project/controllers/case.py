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
from django.db.models import Q, F, Value
from typing import List
from utils.chen_response import ChenResponse
from utils.chen_crud import multi_delete_case
from apps.project.models import Design, Dut, Round, TestDemand, Case, CaseStep, Project, Problem
from apps.project.schemas.case import DeleteSchema, CaseModelOutSchema, CaseFilterSchema, \
    CaseTreeReturnSchema, ReplaceCaseSchema, PersonReplaceSchema, ExetimeReplaceSchema, \
    CaseTreeInputSchema, CaseCreateOutSchema, CaseCreateInputSchema, DemandNodeSchema
from utils.util import get_testType
from utils.codes import HTTP_INDEX_ERROR, HTTP_EXISTS_CASES
from apps.project.tools.copyCase import case_move_to_test, case_copy_to_test, case_to_case_copy_or_move
from utils.smallTools.interfaceTools import conditionNoneToBlank
# 导入case的schema
from apps.project.schemas.case import CaseModelOutSchemaWithoutProblem

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
        if case_id:
            # 当传入了id，则查询单个
            qs = Case.objects.filter(id=case_id)  # type:ignore
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
            qs = Case.objects.filter(**query_params).order_by("key")
        # 由于有嵌套query_set存在，把每个用例的schema加上一个字段
        query_list = []
        for query_single in qs:
            setattr(query_single, "testStep", query_single.step.all().values())
            # 增加一个字段，测试类型例如：FT
            setattr(query_single, 'testType', get_testType(query_single.test.testType, dict_code='testType'))
            # 如果有问题单字段则添加上
            related_problem: Problem = query_single.caseField.first()
            if query_single.caseField.all():
                setattr(query_single, 'problem', related_problem)
            # 2025年5月10日在test字段加上testContent
            test_obj = query_single.test
            sub_list = []
            for step_obj in test_obj.testQField.all():
                setattr(step_obj, "subStep", step_obj.testStepField.all().values())
                sub_list.append(step_obj)
            setattr(test_obj, "testContent", sub_list)
            setattr(query_single, 'test', test_obj)
            query_list.append(query_single)
        return query_list

    @route.get("/getCaseOne", response=CaseModelOutSchemaWithoutProblem, url_name='case-one')
    @transaction.atomic
    def get_case_one(self, key: str, projectId: int):
        """用于在用例树状页面，获取promblem信息，这里根据key获取信息"""
        project_obj = get_object_or_404(Project, id=projectId)
        case = project_obj.pcField.filter(key=key).first()
        if case:
            setattr(case, "testStep", case.step.all().values())
            setattr(case, 'testType', get_testType(case.test.testType, dict_code='testType'))
            return case
        raise HttpError(500, "您获取的数据不存在")

    @route.get("/getCaseOneById", response=CaseModelOutSchemaWithoutProblem, url_name='case-one-by-id')
    @transaction.atomic
    def get_case_by_id(self, id: int):
        """用于在用例树状页面，获取promblem信息，这里根据key获取信息"""
        case = Case.objects.filter(id=id).first()
        if case:
            setattr(case, "testStep", case.step.all().values())
            setattr(case, 'testType', get_testType(case.test.testType, dict_code='testType'))
            return case
        raise HttpError(500, "您获取的数据不存在")

    # 处理树状数据
    @route.get("/getCaseInfo", response=List[CaseTreeReturnSchema], url_name="case-info")
    @transaction.atomic
    def get_case_tree(self, payload: CaseTreeInputSchema = Query(...)):
        qs = Case.objects.filter(project__id=payload.project_id, test__key=payload.key)  # type:ignore
        for q in qs:
            # 遍历每个用例节点，查看是否有关联问题单
            if q.caseField.count() > 0:
                q.isRelatedProblem = True
            # 遍历用例的step查看是否有未通过
            q.isNotPassed = False
            for step in q.step.all():
                if step.passed == '2':
                    q.isNotPassed = True
        return qs

    # 添加测试用例
    @route.post("/case/save", response=CaseCreateOutSchema, url_name="case-create")
    @transaction.atomic
    def create_case(self, payload: CaseCreateInputSchema):
        asert_dict = payload.dict(exclude_none=True)
        # 构造design_key
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
        return qs

    # 更新测试用例
    @route.put("/case/update/{id}", response=CaseCreateOutSchema, url_name="case-update")
    @transaction.atomic
    def update_case(self, id: int, payload: CaseCreateInputSchema):
        # 查到当前
        case_qs = Case.objects.get(id=id)  # type:ignore
        for attr, value in payload.dict().items():
            if attr == 'project_id' or attr == 'round_key' or attr == 'dut_key' or attr == 'design_key' or attr == 'test_key':
                continue
            if attr == 'name':
                setattr(case_qs, "title", value)
            # testStep处理
            if attr == 'testStep':
                content_list = case_qs.step.all()
                for content_single in content_list:
                    content_single.delete()
                data_list = []
                for item in value:
                    if item['operation'] or item['expect'] or item['result'] or item['passed'] or item[
                        'status']:
                        item["case"] = case_qs
                        data_list.append(CaseStep(**item))
                CaseStep.objects.bulk_create(data_list)  # type:ignore

            setattr(case_qs, attr, value)
        # 处理标识-统一设置为YL
        case_qs.ident = case_qs.test.ident
        # ~~~~~~~~~end~~~~~~~~~
        case_qs.save()
        return case_qs

    # 删除测试用例
    @route.delete("/case/delete", url_name="case-delete")
    @transaction.atomic
    def delete_case(self, data: DeleteSchema):
        # 根据其中一个id查询出dut_id，注意这里解决前端框架问题：删除后还报错选择的行id
        try:
            case_single = Case.objects.filter(id=data.ids[0])[0]  # type:ignore
        except IndexError:
            return ChenResponse(status=500, code=HTTP_INDEX_ERROR, message='您未选择需要删除的内容')
        test_id = case_single.test.id
        test_key = case_single.test.key
        multi_delete_case(data.ids, Case)
        index = 0
        case_all_qs = Case.objects.filter(test__id=test_id).order_by('id')  # type:ignore
        for single_qs in case_all_qs:
            case_key = "".join([test_key, '-', str(index)])
            single_qs.key = case_key
            index = index + 1
            single_qs.save()
        return ChenResponse(message="测试用例删除成功！")

    # 右键测试项，根据测试子项生成用例
    @route.post("/case/create_by_demand", url_name='case-create-by-demand')
    def create_case_by_demand(self, demand_node: DemandNodeSchema):
        project_qs = get_object_or_404(Project, id=demand_node.project_id)
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
                # 创建用例步骤
                for demand_step_obj in sub.testStepField.all():
                    operation = demand_step_obj.operation
                    case_step_dict = {
                        'operation': "".join([operation if operation is not None else ""]),
                        'expect': demand_step_obj.expect,
                        'result': '',  # 暂时为空
                        'case': case_model,  # 指定父级Case模型
                    }
                    CaseStep.objects.create(**case_step_dict)  # type:ignore
                index += 1
        # 这里返回一个demand的key用于前端刷新树状图
        return ChenResponse(data={'key': demand_node.key}, status=200, code=200,
                            message='测试项自动生成用例成功')

    # 测试用例复制/移动到测试项上
    @route.get("/case/copy_or_move_to_demand", url_name='case-copy-move-demand')
    @transaction.atomic
    def copy_move_case_to_demand(self, project_id: int, case_key: str, demand_key: str, move: bool):
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
        print(payload)
        # 1.首先查询项目
        project_obj: Project = get_object_or_404(Project, id=payload.project_id)
        # 2.查询[所有轮次]的selectRows的id
        case_qs = project_obj.pcField.filter(id__in=payload.selectRows, round__key=payload.round_key)
        # 3.批量替换里面文本（解构不影响老数组）
        selectColumn = [x for x in payload.selectColumn if x != 'testStep']
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
        # 替换设计人员
        case_qs = Case.objects.filter(id__in=payload.selectRows)
        if payload.designPerson != '不替换' and payload.designPerson != '':
            case_qs.update(designPerson=payload.designPerson)
        if payload.testPerson != '不替换' and payload.testPerson != '':
            case_qs.update(testPerson=payload.testPerson)
        if payload.monitorPerson != '不替换' and payload.monitorPerson != '':
            case_qs.update(monitorPerson=payload.monitorPerson)

    # 批量替换时间
    @route.post("/case/timeReplace/", url_name='case-time-replace')
    @transaction.atomic
    def bulk_replace_time(self, payload: ExetimeReplaceSchema):
        # 替换设计人员
        case_qs = Case.objects.filter(id__in=payload.selectRows)
        case_qs.update(exe_time=payload.exetime)
