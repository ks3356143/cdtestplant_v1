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
from apps.project.models import Design, Dut, Round, TestDemand, TestDemandContent, TestDemandContentStep
from apps.project.schemas.testDemand import DeleteSchema, TestDemandModelOutSchema, TestDemandFilterSchema, \
    TestDemandTreeReturnSchema, TestDemandTreeInputSchema, TestDemandCreateOutSchema, \
    TestDemandCreateInputSchema, ReplaceDemandContentSchema, \
    TestDemandRelatedSchema, TestDemandExistRelatedSchema, DemandCopyToDesignSchema
# 导入ORM
from apps.project.models import Project
# 导入工具
from apps.project.tools.copyDemand import demand_copy_to_design
from apps.project.tools.delete_change_key import demand_delete_sub_node_key
from utils.smallTools.interfaceTools import conditionNoneToBlank

@api_controller("/project", auth=JWTAuth(), permissions=[IsAuthenticated], tags=['测试项接口'])
class TestDemandController(ControllerBase):
    @route.get("/getTestDemandList", response=List[TestDemandModelOutSchema], exclude_none=True,
               url_name="testDemand-list")
    @transaction.atomic
    @paginate(MyPagination)
    def get_test_demand_list(self, datafilter: TestDemandFilterSchema = Query(...)):
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
        qs = TestDemand.objects.filter(**query_params).order_by("key")
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
        demand_qs = TestDemand.objects.filter(project_id=project_id, key=key).first()
        if demand_qs:
            sub_list = []
            for step_obj in demand_qs.testQField.all():
                setattr(step_obj, "subStep", step_obj.testStepField.all().values())
                sub_list.append(step_obj)
            setattr(demand_qs, "testContent", sub_list)
            return demand_qs
        raise HttpError(500, "未找到相应的数据")

    # 根据id直接查询
    @route.get("/getTestDemandOneById", response=TestDemandModelOutSchema, url_name='testDemand-one-by-id')
    @transaction.atomic
    def get_demand_by_id(self, id: int):
        demand_qs = TestDemand.objects.filter(id=id).first()
        if demand_qs:
            sub_list = []
            for step_obj in demand_qs.testQField.all():
                setattr(step_obj, "subStep", step_obj.testStepField.all().values())
                sub_list.append(step_obj)
            setattr(demand_qs, "testContent", sub_list)
            return demand_qs
        raise HttpError(500, "未找到相应的数据")

    # 处理树状数据
    @route.get("/getTestdemandInfo", response=List[TestDemandTreeReturnSchema], url_name="testDemand-info")
    @transaction.atomic
    def get_testDemand_tree(self, payload: TestDemandTreeInputSchema = Query(...)):
        qs = TestDemand.objects.filter(project__id=payload.project_id, design__key=payload.key)
        return qs

    # 添加测试项
    @route.post("/testDemand/save", response=TestDemandCreateOutSchema, url_name="testDemand-create")
    @transaction.atomic
    def create_test_demand(self, payload: TestDemandCreateInputSchema):
        asert_dict = payload.dict(exclude_none=True)
        # ident判重
        project_qs = Project.objects.filter(id=payload.project_id).first()
        if payload.ident and project_qs:
            exists = project_qs.ptField.filter(ident=payload.ident).exists()
            if exists:
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
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # 创建测试项 - 以及子项/子项步骤
        qs = TestDemand.objects.create(**asert_dict)
        for item in payload.dict()['testContent']:
            content_obj = TestDemandContent.objects.create(
                testDemand=qs,
                subName=item['subName']
            )
            TestDemandContentStep.objects.bulk_create([
                TestDemandContentStep(
                    testDemandContent=content_obj,
                    **step.dict() if not isinstance(step, dict) else step
                )
                for step in item['subStep']
            ])
        return qs

    # 更新测试项
    @route.put("/testDemand/update/{id}", response=TestDemandCreateOutSchema, url_name="testDemand-update")
    @transaction.atomic
    def update_testDemand(self, id: int, payload: TestDemandCreateInputSchema):
        project_qs = get_object_or_404(Project, id=payload.project_id)
        # 查到当前
        testDemand_qs = TestDemand.objects.get(id=id)
        old_ident = testDemand_qs.ident  # 用于判断是否要集体修改case的ident
        for attr, value in payload.dict().items():
            # 判重复
            if attr == 'ident':
                if testDemand_qs.ident != value:  # 如果ident不和原来相等，则要判重复
                    exists = project_qs.ptField.filter(ident=payload.ident).exists()
                    if exists:
                        return ChenResponse(code=500, status=500, message='更换的标识和其他测试项重复')
            if attr == 'project_id' or attr == 'round_key' or attr == 'dut_key' or attr == 'design_key':
                continue  # 如果发现是key则不处理
            if attr == 'name':
                setattr(testDemand_qs, "title", value)
            # 找到attr为testContent的
            if attr == 'testContent':
                content_list = testDemand_qs.testQField.all()
                for content_single in content_list:
                    # 删除TestDemandContent，会把CASCADE的TestDemandContentStep也删除
                    content_single.delete()
                # 添加测试项步骤
                for item in value:  # 遍历的是testContent字段,所以每个item是TestDemandContent的数据
                    # 存在subName就添加一个测试子项
                    if item['subName']:
                        content_obj = TestDemandContent.objects.create(
                            testDemand=testDemand_qs,
                            subName=item["subName"]
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
            for case in testDemand_qs.tcField.all():
                case.ident = testDemand_qs.ident
                case.save()
        testDemand_qs.save()
        return testDemand_qs

    # 删除测试项
    @route.delete("/testDemand/delete", url_name="testDemand-delete")
    @transaction.atomic
    def delete_testDemand(self, data: DeleteSchema):
        # 根据其中一个id查询出dut_id
        try:
            test_demand_single = TestDemand.objects.filter(id=data.ids[0])[0]
        except IndexError:
            return ChenResponse(status=500, code=HTTP_INDEX_ERROR, message='您未选择需要删除的内容')
        design_id = test_demand_single.design.id
        design_key = test_demand_single.design.key
        multi_delete_testDemand(data.ids, TestDemand)
        index = 0
        test_demand_all_qs = TestDemand.objects.filter(design__id=design_id).order_by('id')
        for single_qs in test_demand_all_qs:
            test_demand_key = "".join([design_key, '-', str(index)])
            single_qs.key = test_demand_key
            index = index + 1
            single_qs.save()
            demand_delete_sub_node_key(single_qs)  # 删除后需重排子节点
        return ChenResponse(message="测试需求删除成功！")

    # 查询一个项目的所有测试项
    @route.get("/testDemand/getRelatedTestDemand", url_name="testDemand-getRelatedTestDemand")
    @transaction.atomic
    def getRelatedTestDemand(self, id: int, round: str):
        project_qs = get_object_or_404(Project, id=id)
        # 找出属于该轮次的所有测试项
        round_qs = project_qs.pField.filter(key=round).first()
        designs = round_qs.dsField.all()
        data_list = []
        for design in designs:
            design_dict = {'label': design.name, 'value': design.id, 'children': []}
            for test_item in design.dtField.all():
                test_item_dict = {'label': test_item.name, 'value': test_item.id}
                design_dict['children'].append(test_item_dict)
            data_list.append(design_dict)
        return ChenResponse(message='获取成功', data=data_list)

    # 处理desgin关联testDemand接口
    @route.post('/testDemand/solveRelatedTestDemand', url_name="testDemand-solveRelatedTestDemand")
    @transaction.atomic
    def solveRelatedTestDemand(self, data: TestDemandRelatedSchema):
        test_item_ids = data.data
        non_exist_ids = [x for x in test_item_ids]
        project_qs = get_object_or_404(Project, id=data.project_id)
        key_str = "-".join([data.round_key, data.dut_key, data.design_key])
        design_item = project_qs.psField.filter(key=key_str).first()
        if design_item:
            # 将test_item_ids中本身具有的测试项从id数组中移除
            for test_id in test_item_ids:
                for ti in design_item.dtField.all():
                    if ti.pk == test_id:
                        non_exist_ids.remove(test_id)
            if len(non_exist_ids) <= 0 < len(test_item_ids):
                return ChenResponse(status=400, code=200,
                                    message='选择的测试项全部存在于当前设计需求中，请重新选择...')
            # 先查询现在有的关联测试项
            for item in design_item.odField.values('id'):
                item_id = item.get('id', None)
                if not item_id in test_item_ids:
                    test_item_obj = TestDemand.objects.filter(id=item_id).first()
                    design_item.odField.remove(test_item_obj)
            for test_item_id in non_exist_ids:
                test_items = design_item.odField.filter(id=test_item_id)
                if len(test_items) <= 0:
                    # 查询testDemand
                    design_item.odField.add(TestDemand.objects.filter(id=test_item_id).first())
        else:
            return ChenResponse(status=400, code=400, message='设计需求不存在，请检查...')
        return ChenResponse(status=200, code=200, message='添加关联测试项成功...')

    # 找出已关联的测试项给前端的cascader
    @route.post('/testDemand/getExistRelatedTestDemand', url_name="testDemand-getExistRelatedTestDemand")
    @transaction.atomic
    def getExistRelatedTestDemand(self, data: TestDemandExistRelatedSchema):
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
        new_demand_key = demand_copy_to_design(data.project_id, data.demand_key, data.design_id, data.depth)
        return ChenResponse(data={'key': new_demand_key})

    # 测试项-替换接口
    @route.post("/testDemand/replace/", url_name='testDemand-replace')
    @transaction.atomic
    def replace_demand_content(self, payload: ReplaceDemandContentSchema):
        # 1.首先查询项目
        project_obj: Project = get_object_or_404(Project, id=payload.project_id)
        # 2.查询[所有轮次]的selectRows的id
        demand_qs = project_obj.ptField.filter(id__in=payload.selectRows, round__key=payload.round_key)
        # 3.批量替换里面文本（解构不影响老数组）
        selectColumn = [x for x in payload.selectColumn if x != 'testContent']
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
