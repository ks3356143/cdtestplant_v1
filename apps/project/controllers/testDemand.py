from ninja_extra import api_controller, ControllerBase, route
from ninja import Query
from ninja_jwt.authentication import JWTAuth
from ninja_extra.permissions import IsAuthenticated
from ninja.pagination import paginate
from ninja.errors import HttpError
from utils.chen_pagination import MyPagination
from django.db import transaction
from django.db.models.functions import Replace
from django.db.models import Q, F, Value
from django.shortcuts import get_object_or_404
from typing import List
from utils.chen_response import ChenResponse
from utils.chen_crud import multi_delete_testDemand
from utils.codes import HTTP_INDEX_ERROR
from apps.project.tools.access_control import (check_project_access, check_project_access_by_id,
                                               check_objects_access, get_object_in_project)
from apps.project.models import Design, Dut, Round, TestDemand, TestDemandContent, TestDemandContentStep, Project, Case
from apps.project.schemas.testDemand import DeleteSchema, TestDemandModelOutSchema, TestDemandFilterSchema, \
    TestDemandTreeReturnSchema, TestDemandTreeInputSchema, TestDemandCreateOutSchema, \
    TestDemandCreateInputSchema, ReplaceDemandContentSchema, PriorityReplaceSchema, \
    TestDemandRelatedSchema, TestDemandExistRelatedSchema, DemandCopyToDesignSchema, \
    TestDemandMultiCreateInputSchema
# 导入工具
from apps.project.tools.copyDemand import demand_copy_to_design
from apps.project.tools.delete_change_key import demand_delete_sub_node_key
from utils.smallTools.interfaceTools import conditionNoneToBlank
from apps.project.tool.batchTools import parse_test_content_string

# 批量替换允许的文本字段白名单
DEMAND_REPLACE_FIELDS = {'ident', 'name', 'title', 'adequacy', 'testDesciption'}

@api_controller("/project", auth=JWTAuth(), permissions=[IsAuthenticated], tags=['测试项接口'])
class TestDemandController(ControllerBase):
    @route.get("/getTestDemandList", response=List[TestDemandModelOutSchema], exclude_none=True,
               url_name="testDemand-list")
    @transaction.atomic
    @paginate(MyPagination)
    def get_test_demand_list(self, datafilter: TestDemandFilterSchema = Query(...)):
        check_project_access_by_id(datafilter.project_id, self.context.request.user)
        conditionNoneToBlank(datafilter)
        query_params = {
            'project__id': datafilter.project_id,
            'ident__icontains': datafilter.ident,
            'name__icontains': datafilter.name,
            'testType__contains': datafilter.testType,
            'priority__icontains': datafilter.priority
        }
        # 如果没有传递多个key则认为是“那个轮次汇总界面”
        if datafilter.dut_id and datafilter.design_id:
            design_key = "".join([datafilter.round_id, '-', datafilter.dut_id, '-', datafilter.design_id])
            query_params['design__key'] = design_key
        else:
            # 轮次汇总界面要查round__key
            query_params['round__key'] = datafilter.round_id
        # 判断是否存在testDesciption有则表示是大表查询
        if datafilter.testDesciption:
            query_params['testDesciption__icontains'] = datafilter.testDesciption
        qs = TestDemand.objects.filter(**query_params).order_by("key").prefetch_related('testQField')
        # 判断是否存在testContent有则表示是大表查询，这里需要查询子字段
        if datafilter.testContent:
            qs = qs.filter(Q(testQField__subName__icontains=datafilter.testContent) |
                           Q(testQField__testStepField__operation__icontains=datafilter.testContent) |
                           Q(testQField__testStepField__expect__icontains=datafilter.testContent))
        # 由于有嵌套query_set存在，把每个测试需求的schema加上一个字段
        query_list = []
        for query_single in qs:
            # 遍历每一个测试子项
            sub_list = []
            for step_obj in query_single.testQField.all():
                setattr(step_obj, "subStep", step_obj.testStepField.all().values())
                sub_list.append(step_obj)
            setattr(query_single, "testContent", sub_list)
            query_list.append(query_single)
        return query_list

    @route.get("/getTestDemandOne", response=TestDemandModelOutSchema, url_name='testDemand-one')
    @transaction.atomic
    def get_test_demand_one(self, project_id: int, key: str):
        check_project_access_by_id(project_id, self.context.request.user)
        demand_qs = TestDemand.objects.filter(project_id=project_id, key=key).first()
        if demand_qs:
            sub_list = []
            for step_obj in demand_qs.testQField.all():
                setattr(step_obj, "subStep", step_obj.testStepField.all().values())
                sub_list.append(step_obj)
            setattr(demand_qs, "testContent", sub_list)
            return demand_qs
        raise HttpError(404, "未找到相应的数据")

    # 根据id直接查询
    @route.get("/getTestDemandOneById", response=TestDemandModelOutSchema, url_name='testDemand-one-by-id')
    @transaction.atomic
    def get_demand_by_id(self, id: int):
        demand_qs = TestDemand.objects.filter(id=id).first()
        if demand_qs:
            check_project_access(demand_qs.project, self.context.request.user)
        if demand_qs:
            sub_list = []
            for step_obj in demand_qs.testQField.all():
                setattr(step_obj, "subStep", step_obj.testStepField.all().values())
                sub_list.append(step_obj)
            setattr(demand_qs, "testContent", sub_list)
            return demand_qs
        raise HttpError(404, "未找到相应的数据")

    # 处理树状数据
    @route.get("/getTestdemandInfo", response=List[TestDemandTreeReturnSchema], url_name="testDemand-info")
    @transaction.atomic
    def get_testDemand_tree(self, payload: TestDemandTreeInputSchema = Query(...)):
        check_project_access_by_id(payload.project_id, self.context.request.user)
        qs = TestDemand.objects.filter(project__id=payload.project_id, design__key=payload.key)
        return qs

    # 添加测试项
    @route.post("/testDemand/save", response=TestDemandCreateOutSchema, url_name="testDemand-create")
    @transaction.atomic
    def create_test_demand(self, payload: TestDemandCreateInputSchema):
        check_project_access_by_id(payload.project_id, self.context.request.user)
        asert_dict = payload.dict(exclude_none=True)
        # ident判重
        project_qs = Project.objects.filter(id=payload.project_id).first()
        if payload.ident and project_qs:
            old_obj = project_qs.ptField.filter(ident=payload.ident).first()
            # 2025/06/24修改，现在运行不同测试类型有相同的标识
            if old_obj and old_obj.testType == payload.testType:
                return ChenResponse(code=500, status=500,
                                    message='测试项标识和其他测试项重复，请更换测试项标识!!!')
        # 构造design_key
        design_key = "".join([payload.round_key, "-", payload.dut_key, '-', payload.design_key])
        # 查询当前key应该为多少
        test_demand_count = TestDemand.objects.filter(project__id=payload.project_id,
                                                      design__key=design_key).count()
        key_string = ''.join([design_key, "-", str(test_demand_count)])
        # 查询当前各个前面节点的instance
        round_instance = Round.objects.get(project__id=payload.project_id, key=payload.round_key)
        dut_instance = Dut.objects.get(project__id=payload.project_id,
                                       key="".join([payload.round_key, "-", payload.dut_key]))
        design_instance = Design.objects.get(project__id=payload.project_id, key="".join(
            [payload.round_key, "-", payload.dut_key, '-', payload.design_key]))
        asert_dict.update(
            {'key': key_string, 'round': round_instance, 'dut': dut_instance, 'design': design_instance,
             'title': payload.name})
        asert_dict.pop("round_key")
        asert_dict.pop("dut_key")
        asert_dict.pop("design_key")
        asert_dict.pop("testContent")
        # 创建测试项 - 以及子项/子项步骤
        qs = TestDemand.objects.create(**asert_dict)
        for item in payload.dict()['testContent']:
            content_obj = TestDemandContent.objects.create(
                testDemand=qs,
                subName=item['subName'],
                subDescription=item['subDescription']
            )
            TestDemandContentStep.objects.bulk_create([
                TestDemandContentStep(
                    testDemandContent=content_obj,
                    **step.dict() if not isinstance(step, dict) else step
                )
                for step in item['subStep']
            ])
        return qs

    # 批量新增测试项
    @route.post("/testDemand/multi_save", url_name="testDemand-multi-create")
    @transaction.atomic
    def create_multi_test_demand(self, payload: TestDemandMultiCreateInputSchema):
        # 访问控制：与其它写接口保持一致，防止跨项目写入（自主访问控制 7.1.3）
        check_project_access_by_id(payload.project_id, self.context.request.user)
        # 1.首先判断测试项标识是否重复
        project_qs = Project.objects.filter(id=payload.project_id).first()
        if not project_qs:
            return ChenResponse(code=400, status=400, message='项目不存在，请检查')
        designs = project_qs.psField.all()
        ## 给返回response的data数据以便前端更新树状目录
        keys = []
        ## 遍历payload.demands数组
        for index, demandOne in enumerate(payload.demands):
            if demandOne.ident and project_qs:
                old_obj = project_qs.ptField.filter(ident=demandOne.ident).first()
                if old_obj and old_obj.testType == demandOne.testType:
                    message_temp = f"第{index}个测试项标识重复，请修改"
                    return ChenResponse(status=200, code=500101, data=index, message=message_temp)
        # 标识不重复就开始录入了
        for index, demand in enumerate(payload.demands):
            create_sub_demands = parse_test_content_string(demand.testContent)
            if isinstance(create_sub_demands, ChenResponse):
                return create_sub_demands
            else:
                # 这说明解析成功了
                # 首先查询所属design、dut、round，方便新增
                design_obj: Design = designs.filter(key=demand.parent_key).first()  # 因为前端限制必然有
                dut_obj = design_obj.dut
                round_obj = design_obj.round
                test_demand_count = TestDemand.objects.filter(project=project_qs,
                                                              design=design_obj).count()
                key_string = ''.join([design_obj.key, "-", str(test_demand_count)])
                keys.append(key_string)
                create_demand_dict = {
                    'ident': demand.ident,
                    'name': demand.name,
                    'adequacy': demand.adequacy,
                    'priority': demand.priority,
                    'testType': demand.testType,
                    'testMethod': demand.testMethod,
                    'title': demand.name,
                    'key': key_string,
                    'project': project_qs,
                    'round': round_obj,
                    'dut': dut_obj,
                    'design': design_obj,
                    'testDesciption': demand.testDesciption
                }
                demand_created = TestDemand.objects.create(**create_demand_dict)
                # 录入测试子项
                for sub in create_sub_demands:
                    content_obj = TestDemandContent.objects.create(
                        testDemand=demand_created,
                        subName=sub['subName'],
                        subDescription=sub['subDescription']
                    )
                    TestDemandContentStep.objects.bulk_create([
                        TestDemandContentStep(
                            testDemandContent=content_obj,
                            **step.dict() if not isinstance(step, dict) else step
                        )
                        for step in sub['subStep']
                    ])
        return ChenResponse(code=200991, status=200, data=keys, message='成功录入')

    # 更新测试项
    @route.put("/testDemand/update/{id}", response=TestDemandCreateOutSchema, url_name="testDemand-update")
    @transaction.atomic
    def update_testDemand(self, id: int, payload: TestDemandCreateInputSchema):
        # 目标测试项必须属于 payload 指定的项目
        testDemand_qs = get_object_in_project(TestDemand, id, payload.project_id, self.context.request.user)
        project_qs = get_object_or_404(Project, id=payload.project_id)
        old_ident = testDemand_qs.ident  # 用于判断是否要集体修改case的ident
        for attr, value in payload.dict().items():
            # 判重复：同项目、同测试类型的测试项标识不可重复（排除自身，空标识不校验）
            if attr == 'ident' and value:
                duplicate = project_qs.ptField.filter(
                    ident=value, testType=payload.dict()['testType']).exclude(id=id)
                # 2025/06/24修改：不同类型可以相同
                if duplicate.exists():
                    return ChenResponse(code=500, status=500, message='更换的标识和其他测试项重复')
            if attr == 'project_id' or attr == 'round_key' or attr == 'dut_key' or attr == 'design_key':
                continue  # 如果发现是key则不处理
            if attr == 'name':
                setattr(testDemand_qs, "title", value)
            # 找到attr为testContent的
            if attr == 'testContent':
                # 删除 TestDemandContent 时其下 TestDemandContentStep 会级联删除
                testDemand_qs.testQField.all().delete()
                # 添加测试项步骤
                for item in value:  # 遍历的是testContent字段,所以每个item是TestDemandContent的数据
                    # 存在subName就添加一个测试子项
                    if item['subName']:
                        content_obj = TestDemandContent.objects.create(
                            testDemand=testDemand_qs,
                            subName=item["subName"],
                            subDescription=item["subDescription"]
                        )
                        TestDemandContentStep.objects.bulk_create([
                            TestDemandContentStep(
                                testDemandContent=content_obj,
                                **step.dict() if not isinstance(step, dict) else step
                            )
                            for step in item["subStep"]
                        ])
            setattr(testDemand_qs, attr, value)
        # ~~~2024年5月9日：测试项更新标识后还要更新下面用例的标识~~~
        if testDemand_qs.ident != old_ident:
            # 批量更新下级用例标识（Case 为完整性受保护模型，显式补刷标签）
            cases = list(testDemand_qs.tcField.all())
            for case in cases:
                case.ident = testDemand_qs.ident
            if cases:
                from apps.project.tools.integrity import refresh_tags
                Case.objects.bulk_update(cases, ['ident'])
                refresh_tags(cases)
        testDemand_qs.save()
        return testDemand_qs

    # 删除测试项
    @route.delete("/testDemand/delete", url_name="testDemand-delete")
    @transaction.atomic
    def delete_testDemand(self, data: DeleteSchema):
        # 逐个校验每条选中测试项的项目归属（原先只校验第一行，其余行可跨项目删除）
        demand_objs = check_objects_access(TestDemand, data.ids, self.context.request.user)
        affected = {(obj.design_id, obj.design.key) for obj in demand_objs}
        multi_delete_testDemand([obj.id for obj in demand_objs], TestDemand)
        for design_id, design_key in affected:
            index = 0
            test_demand_all_qs = TestDemand.objects.filter(design__id=design_id).order_by('id')
            for single_qs in test_demand_all_qs:
                test_demand_key = "".join([design_key, '-', str(index)])
                single_qs.key = test_demand_key
                index = index + 1
                single_qs.save()
                demand_delete_sub_node_key(single_qs)  # 删除后需重排子节点
        return ChenResponse(message="测试需求删除成功！")

    # 查询一个项目的所有测试项【当前轮次】
    @route.get("/testDemand/getRelatedTestDemand", url_name="testDemand-getRelatedTestDemand")
    @transaction.atomic
    def getRelatedTestDemand(self, id: int, round: str):
        check_project_access_by_id(id, self.context.request.user)
        project_qs = get_object_or_404(Project, id=id)
        # 找出属于该轮次的所有测试项
        round_qs = project_qs.pField.filter(key=round).first()
        if not round_qs:
            return ChenResponse(status=400, code=400, message='轮次不存在，请检查...')
        designs = round_qs.dsField.all()
        data_list = []
        for design in designs:
            design_dict = {'label': design.name, 'value': design.id, 'children': []}
            for test_item in design.dtField.all():
                test_item_dict = {'label': test_item.name, 'value': test_item.id, 'key': test_item.key}
                design_dict['children'].append(test_item_dict)
            data_list.append(design_dict)
        return ChenResponse(message='获取成功', data=data_list)

    # 处理desgin关联testDemand接口
    @route.post('/testDemand/solveRelatedTestDemand', url_name="testDemand-solveRelatedTestDemand")
    @transaction.atomic
    def solveRelatedTestDemand(self, data: TestDemandRelatedSchema):
        test_item_ids = data.data
        check_project_access_by_id(data.project_id, self.context.request.user)
        project_qs = get_object_or_404(Project, id=data.project_id)
        key_str = "-".join([data.round_key, data.dut_key, data.design_key])
        design_item = project_qs.psField.filter(key=key_str).first()
        if design_item:
            # 只允许关联当前项目内的测试项，防止把别的项目的测试项挂到本项目
            valid_ids = set(TestDemand.objects.filter(project=project_qs, id__in=test_item_ids)
                            .values_list('id', flat=True))
            invalid_ids = [i for i in test_item_ids if i not in valid_ids]
            if invalid_ids:
                return ChenResponse(status=400, code=400,
                                    message=f'测试项不属于当前项目或不存在，已拒绝：{invalid_ids}')
            # 将test_item_ids中本身具有的测试项从id数组中移除
            direct_ids = set(design_item.dtField.values_list('id', flat=True))
            non_exist_ids = [test_id for test_id in test_item_ids if test_id not in direct_ids]
            if len(non_exist_ids) <= 0 < len(test_item_ids):
                return ChenResponse(status=400, code=200,
                                    message='选择的测试项全部存在于当前设计需求中，请重新选择...')
            # 一次性替换“其他关联测试项”集合：set 内部完成 remove + add，避免 O(n·m) 双层循环
            design_item.odField.set([i for i in valid_ids if i not in direct_ids])
            return ChenResponse(status=200, code=200, message='添加关联测试项成功...')
        else:
            return ChenResponse(status=400, code=400, message='设计需求不存在，请检查...')

    # 找出已关联的测试项给前端的cascader
    @route.post('/testDemand/getExistRelatedTestDemand', url_name="testDemand-getExistRelatedTestDemand")
    @transaction.atomic
    def getExistRelatedTestDemand(self, data: TestDemandExistRelatedSchema):
        check_project_access_by_id(data.project_id, self.context.request.user)
        project_qs = get_object_or_404(Project, id=data.project_id)
        key_str = "-".join([data.round_key, data.dut_key, data.design_key])
        design_item = project_qs.psField.filter(key=key_str).first()
        ids = []
        if design_item:
            for item in design_item.odField.all():
                ids.append(item.id)
        return ids

    # 前端测试项右键复制到某个设计需求下面
    @route.post('/testDemand/copy_to_design', url_name='testDemand-copy')
    @transaction.atomic
    def copy_to_design(self, data: DemandCopyToDesignSchema):
        """前端测试项右键复制到某个设计需求下面"""
        check_project_access_by_id(data.project_id, self.context.request.user)
        new_demand_key = demand_copy_to_design(data.project_id, data.demand_key, data.design_id, data.depth)
        return ChenResponse(data={'key': new_demand_key})

    # 测试项-替换接口
    @route.post("/testDemand/replace/", url_name='testDemand-replace')
    @transaction.atomic
    def replace_demand_content(self, payload: ReplaceDemandContentSchema):
        check_project_access_by_id(payload.project_id, self.context.request.user)
        # 1.首先查询项目
        project_obj: Project = get_object_or_404(Project, id=payload.project_id)
        # 2.查询[所有轮次]的selectRows的id
        demand_qs = project_obj.ptField.filter(id__in=payload.selectRows, round__key=payload.round_key)
        # 3.批量替换里面文本（解构不影响老数组）
        selectColumn = [x for x in payload.selectColumn if x != 'testContent']
        unknown = [x for x in selectColumn if x not in DEMAND_REPLACE_FIELDS]
        if unknown:
            return ChenResponse(status=400, code=400, message=f'不支持替换的字段：{unknown}')
        replace_kwargs = {
            field_name: Replace(F(field_name), Value(payload.originText), Value(payload.replaceText))
            for field_name in selectColumn
        }
        # 4.单独处理testContentStep的操作、预期-查询所有
        # 4.1.获取所有关联的TestDemandContentStep
        step_count = 0
        if 'testContent' in payload.selectColumn:
            test_demand_contents = TestDemandContent.objects.filter(testDemand__in=demand_qs)
            test_steps = TestDemandContentStep.objects.filter(testDemandContent__in=test_demand_contents)
            # 批量更新 operation 和 expect
            step_count = test_steps.update(
                operation=Replace(F('operation'), Value(payload.originText), Value(payload.replaceText)),
                expect=Replace(F('expect'), Value(payload.originText), Value(payload.replaceText))
            )
        # 5.提交更新
        replace_count = demand_qs.update(**replace_kwargs)
        return {'count': replace_count + step_count}

    # 批量替换优先级-priority
    @route.post("/testDemand/priorityReplace/", url_name='demand-priority-replace')
    @transaction.atomic
    def multiple_modify_demand_priority(self, payload: PriorityReplaceSchema):
        check_project_access_by_id(payload.project_id, self.context.request.user)
        # 只改当前项目内的测试项，防止跨项目批量改优先级
        demand_qs = TestDemand.objects.filter(id__in=payload.selectRows, project_id=payload.project_id)
        affected = demand_qs.count()
        if affected != len(set(payload.selectRows)):
            return ChenResponse(status=400, code=400,
                                message='部分测试项不属于当前项目或已被删除，已拒绝批量修改')
        demand_qs.update(priority=payload.priority)
        return ChenResponse(message="批量替换优先级成功", data={'count': affected})
