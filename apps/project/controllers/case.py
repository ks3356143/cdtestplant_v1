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
from apps.project.models import Design, Dut, Round, TestDemand, TestDemandContent, Case, CaseStep
from apps.project.schemas.case import DeleteSchema, CaseModelOutSchema, CaseFilterSchema, CaseTreeReturnSchema, \
    CaseTreeInputSchema, CaseTreeInputSchema, CaseCreateOutSchema, CaseCreateInputSchema

@api_controller("/project", auth=JWTAuth(), permissions=[IsAuthenticated], tags=['测试用例接口'])
class CaseController(ControllerBase):
    @route.get("/getCaseList", response=List[CaseModelOutSchema], exclude_none=True,
               url_name="case-list")
    @transaction.atomic
    @paginate(MyPagination)
    def get_case_list(self, data: CaseFilterSchema = Query(...)):
        for attr, value in data.__dict__.items():
            if getattr(data, attr) is None:
                setattr(data, attr, '')
        test_key = "".join([data.round_id, '-', data.dut_id, '-', data.design_id, '-', data.test_id])
        qs = Case.objects.filter(project__id=data.project_id, test__key=test_key,
                                 ident__icontains=data.ident,
                                 name__icontains=data.name,
                                 designPerson__icontains=data.designPerson,
                                 testPerson__icontains=data.testPerson,
                                 monitorPerson__icontains=data.monitorPerson,
                                 summarize__icontains=data.summarize,
                                 ).order_by("key")
        # 由于有嵌套query_set存在，把每个用例的schema加上一个字段
        query_list = []
        for query_single in qs:
            setattr(query_single, "testStep", query_single.step.all().values())
            query_list.append(query_single)
        return query_list

    # 处理树状数据
    @route.get("/getCaseInfo", response=List[CaseTreeReturnSchema], url_name="case-info")
    @transaction.atomic
    def get_case_tree(self, payload: CaseTreeInputSchema = Query(...)):
        qs = Case.objects.filter(project__id=payload.project_id, test__key=payload.key)
        return qs

    # 添加测试用例
    @route.post("/case/save", response=CaseCreateOutSchema, url_name="case-create")
    @transaction.atomic
    def create_case(self, payload: CaseCreateInputSchema):
        asert_dict = payload.dict(exclude_none=True)
        # 构造design_key
        test_whole_key = "".join(
            [payload.round_key, "-", payload.dut_key, '-', payload.design_key, '-', payload.test_key])
        # 判重标识-不需要再查询round以后的
        if Case.objects.filter(project__id=payload.project_id, round__key=payload.round_key,
                               test__key=test_whole_key,
                               ident=payload.ident).exists():
            return ChenResponse(code=400, status=400, message='测试用例的标识重复，请检查')
        # 查询当前key应该为多少
        case_count = Case.objects.filter(project__id=payload.project_id, test__key=test_whole_key).count()
        key_string = ''.join([test_whole_key, "-", str(case_count)])
        # 查询当前各个前面节点的instance
        round_instance = Round.objects.get(project__id=payload.project_id, key=payload.round_key)
        dut_instance = Dut.objects.get(project__id=payload.project_id,
                                       key="".join([payload.round_key, "-", payload.dut_key]))
        design_instance = Design.objects.get(project__id=payload.project_id, key="".join(
            [payload.round_key, "-", payload.dut_key, '-', payload.design_key]))
        test_instance = TestDemand.objects.get(project__id=payload.project_id, key="".join(
            [payload.round_key, "-", payload.dut_key, '-', payload.design_key, '-', payload.test_key]))
        asert_dict.update({'key': key_string, 'round': round_instance, 'dut': dut_instance, 'design': design_instance,
                           "test": test_instance, 'title': payload.name})
        asert_dict.pop("round_key")
        asert_dict.pop("dut_key")
        asert_dict.pop("design_key")
        asert_dict.pop("test_key")
        asert_dict.pop("testStep")
        qs = Case.objects.create(**asert_dict)
        # 对testStep单独处理
        data_list = []
        for item in payload.dict()["testStep"]:
            if not isinstance(item, dict):
                item = item.dict()
            item["case"] = qs
            data_list.append(CaseStep(**item))
        CaseStep.objects.bulk_create(data_list)
        return ChenResponse(code=200, status=200, message="新增测试用例成功!")

    # 更新测试用例
    @route.put("/case/update/{id}", url_name="case-update")
    @transaction.atomic
    def update_case(self, id: int, payload: CaseCreateInputSchema):
        test_case_search = Case.objects.filter(project__id=payload.project_id, ident=payload.ident)
        # 判断是否和同项目同轮次的标识重复
        if len(test_case_search) > 1:
            return ChenResponse(code=400, status=400, message='测试用例的标识重复，请检查')
        # 查到当前
        case_qs = Case.objects.get(id=id)
        for attr, value in payload.dict().items():
            if attr == 'project_id' or attr == 'round_key' or attr == 'dut_key' or attr == 'design_key' or attr == 'test_key':
                continue
            if attr == 'name':
                setattr(case_qs, "title", value)
            # 找到attr为testContent的
            if attr == 'testStep':
                index = 0
                for item in value:
                    cs = case_qs.step.all()[index]
                    setattr(cs, "operation", item["operation"])
                    setattr(cs, "expect", item["expect"])
                    setattr(cs, "result", item["result"])
                    setattr(cs, "passed", item["passed"])
                    setattr(cs, "status", item["status"])
                    cs.save()
                    index = index + 1
            setattr(case_qs, attr, value)
        case_qs.save()
        return ChenResponse(message="用例更新成功!")

    # 删除测试用例
    @route.delete("/case/delete", url_name="case-delete")
    @transaction.atomic
    def delete_case(self, data: DeleteSchema):
        # 根据其中一个id查询出dut_id
        case_single = Case.objects.filter(id=data.ids[0])[0]
        test_id = case_single.test.id
        test_key = case_single.test.key
        multi_delete(data.ids, Case)
        index = 0
        case_all_qs = Case.objects.filter(test__id=test_id)
        for single_qs in case_all_qs:
            case_key = "".join([test_key, '-', str(index)])
            single_qs.key = case_key
            index = index + 1
            single_qs.save()
        return ChenResponse(message="测试用例删除成功！")
