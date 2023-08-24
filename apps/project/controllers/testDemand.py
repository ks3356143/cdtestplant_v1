from ninja_extra import api_controller, ControllerBase, route
from ninja import Query
from ninja_jwt.authentication import JWTAuth
from ninja_extra.permissions import IsAuthenticated
from ninja.pagination import paginate
from utils.chen_pagination import MyPagination
from django.db import transaction
from typing import List
from utils.chen_response import ChenResponse
from utils.chen_crud import multi_delete
from apps.project.models import Design, Dut, Round, TestDemand, TestDemandContent
from apps.project.schemas.testDemand import DeleteSchema, TestDemandModelOutSchema, TestDemandFilterSchema, \
    TestDemandTreeReturnSchema, TestDemandTreeInputSchema, TestDemandCreateOutSchema, TestDemandCreateInputSchema

@api_controller("/project", auth=JWTAuth(), permissions=[IsAuthenticated], tags=['测试项接口'])
class TestDemandController(ControllerBase):
    @route.get("/getTestDemandList", response=List[TestDemandModelOutSchema], exclude_none=True,
               url_name="testDemand-list")
    @transaction.atomic
    @paginate(MyPagination)
    def get_test_demand_list(self, datafilter: TestDemandFilterSchema = Query(...)):
        for attr, value in datafilter.__dict__.items():
            if getattr(datafilter, attr) is None:
                setattr(datafilter, attr, '')
        design_key = "".join([datafilter.round_id, '-', datafilter.dut_id, '-', datafilter.design_id])
        qs = TestDemand.objects.filter(project__id=datafilter.project_id, design__key=design_key,
                                       ident__icontains=datafilter.ident,
                                       name__icontains=datafilter.name,
                                       testType__contains=datafilter.testType,
                                       priority__icontains=datafilter.priority).order_by("key")
        # 由于有嵌套query_set存在，把每个测试需求的schema加上一个字段
        query_list = []
        for query_single in qs:
            setattr(query_single, "testContent", query_single.testQField.all().values())
            query_list.append(query_single)
        return query_list

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
        # 构造design_key
        design_key = "".join([payload.round_key, "-", payload.dut_key, '-', payload.design_key])
        # 查询当前key应该为多少
        test_demand_count = TestDemand.objects.filter(project__id=payload.project_id, design__key=design_key).count()
        key_string = ''.join([design_key, "-", str(test_demand_count)])
        # 查询当前各个前面节点的instance
        round_instance = Round.objects.get(project__id=payload.project_id, key=payload.round_key)
        dut_instance = Dut.objects.get(project__id=payload.project_id,
                                       key="".join([payload.round_key, "-", payload.dut_key]))
        design_instance = Design.objects.get(project__id=payload.project_id, key="".join(
            [payload.round_key, "-", payload.dut_key, '-', payload.design_key]))
        asert_dict.update({'key': key_string, 'round': round_instance, 'dut': dut_instance, 'design': design_instance,
                           'title': payload.name})
        asert_dict.pop("round_key")
        asert_dict.pop("dut_key")
        asert_dict.pop("design_key")
        asert_dict.pop("testContent")
        # 对标识进行处理，获取设计需求的标识，然后存入例如RS422
        asert_dict['ident'] = design_instance.ident
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        qs = TestDemand.objects.create(**asert_dict)
        # 对testContent单独处理
        data_list = []
        for item in payload.dict()["testContent"]:
            if not isinstance(item, dict):
                item = item.dict()
            item["testDemand"] = qs
            data_list.append(TestDemandContent(**item))
        TestDemandContent.objects.bulk_create(data_list)
        return qs

    # 更新测试需求
    @route.put("/testDemand/update/{id}", response=TestDemandCreateOutSchema, url_name="testDemand-update")
    @transaction.atomic
    def update_testDemand(self, id: int, payload: TestDemandCreateInputSchema):
        # 查到当前
        testDemand_qs = TestDemand.objects.get(id=id)
        for attr, value in payload.dict().items():
            if attr == 'project_id' or attr == 'round_key' or attr == 'dut_key' or attr == 'design_key':
                continue
            if attr == 'name':
                setattr(testDemand_qs, "title", value)
            # 找到attr为testContent的
            if attr == 'testContent':
                content_list = testDemand_qs.testQField.all()
                for content_single in content_list:
                    content_single.delete()
                # 添加测试项步骤
                data_list = []
                for item in value:
                    if item['testXuQiu'] or item['testYuQi']:
                        item["testDemand"] = testDemand_qs
                        data_list.append(TestDemandContent(**item))
                TestDemandContent.objects.bulk_create(data_list)
            setattr(testDemand_qs, attr, value)
        testDemand_qs.save()
        return testDemand_qs

    # 删除测试需求
    @route.delete("/testDemand/delete", url_name="design-delete")
    @transaction.atomic
    def delete_testDemand(self, data: DeleteSchema):
        # 根据其中一个id查询出dut_id
        test_demand_single = TestDemand.objects.filter(id=data.ids[0])[0]
        design_id = test_demand_single.design.id
        design_key = test_demand_single.design.key
        multi_delete(data.ids, TestDemand)
        index = 0
        test_demand_all_qs = TestDemand.objects.filter(design__id=design_id)
        for single_qs in test_demand_all_qs:
            test_demand_key = "".join([design_key, '-', str(index)])
            single_qs.key = test_demand_key
            index = index + 1
            single_qs.save()
        return ChenResponse(message="测试需求删除成功！")
