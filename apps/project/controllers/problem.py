import numpy as np
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
from apps.project.models import Design, Dut, Round, TestDemand, TestDemandContent, Case, CaseStep, Problem
from apps.project.schemas.problem import DeleteSchema, ProblemModelOutSchema, ProblemFilterSchema, \
    ProblemTreeReturnSchema, ProblemTreeInputSchema, ProblemCreateOutSchema, ProblemCreateInputSchema, \
    ProblemSingleInputSchema

@api_controller("/project", auth=JWTAuth(), permissions=[IsAuthenticated], tags=['测试用例接口'])
class ProblemController(ControllerBase):
    @route.get("/getProblemList", response=List[ProblemModelOutSchema], exclude_none=True,
               url_name="problem-list")
    @transaction.atomic
    @paginate(MyPagination)
    def get_problem_list(self, data: ProblemFilterSchema = Query(...)):
        for attr, value in data.__dict__.items():
            if getattr(data, attr) is None:
                setattr(data, attr, '')

        case_key = "".join([data.round_id, '-', data.dut_id, '-', data.design_id, '-', data.test_id, '-', data.case_id])
        qs = Problem.objects.filter(project__id=data.project_id, case__key=case_key,
                                    ident__icontains=data.ident,
                                    name__icontains=data.name,
                                    status__icontains=data.status,
                                    type__icontains=data.type,
                                    grade__icontains=data.grade,
                                    operation__icontains=data.operation,
                                    postPerson__icontains=data.postPerson,
                                    ).order_by("key")
        # 遍历通过代码不通过ORM查询闭环方式-巧妙使用numpy中array对象的in方法来判断
        closeMethod1 = self.context.request.GET.get("closeMethod[0]")
        closeMethod2 = self.context.request.GET.get("closeMethod[1]")
        query_final = []
        for query in qs:
            arr = np.array(query.closeMethod)
            if closeMethod1 is None and closeMethod2 is None:
                query_final.append(query)
                continue
            if closeMethod1 in arr:
                query_final.append(query)
                continue
            if closeMethod2 in arr:
                query_final.append(query)
                continue
        return query_final

    # 处理树状数据
    @route.get("/getProblemInfo", response=List[ProblemTreeReturnSchema], url_name="problem-info")
    @transaction.atomic
    def get_case_tree(self, payload: ProblemTreeInputSchema = Query(...)):
        qs = Problem.objects.filter(project__id=payload.project_id, case__key=payload.key)
        return qs

    # 添加问题单
    @route.post("/problem/save", response=ProblemCreateOutSchema, url_name="problem-create")
    @transaction.atomic
    def create_case_demand(self, payload: ProblemCreateInputSchema):
        asert_dict = payload.dict(exclude_none=True)
        # 构造design_key
        problem_whole_key = "".join(
            [payload.round_key, "-", payload.dut_key, '-', payload.design_key, '-', payload.test_key, '-',
             payload.case_key])
        # 判重标识-不需要再查询round以后的
        if Case.objects.filter(project__id=payload.project_id, round__key=payload.round_key,
                               test__key=problem_whole_key,
                               ident=payload.ident).exists():
            return ChenResponse(code=400, status=400, message='被测件的标识重复，请检查')
        # 查询当前key应该为多少
        problem_count = Problem.objects.filter(project__id=payload.project_id, case__key=problem_whole_key).count()
        key_string = ''.join([problem_whole_key, "-", str(problem_count)])
        # 查询当前各个前面节点的instance
        round_instance = Round.objects.get(project__id=payload.project_id, key=payload.round_key)
        dut_instance = Dut.objects.get(project__id=payload.project_id,
                                       key="".join([payload.round_key, "-", payload.dut_key]))
        design_instance = Design.objects.get(project__id=payload.project_id, key="".join(
            [payload.round_key, "-", payload.dut_key, '-', payload.design_key]))
        test_instance = TestDemand.objects.get(project__id=payload.project_id, key="".join(
            [payload.round_key, "-", payload.dut_key, '-', payload.design_key, '-', payload.test_key]))
        case_instance = Case.objects.get(project__id=payload.project_id, key="".join(
            [payload.round_key, "-", payload.dut_key, '-', payload.design_key, '-', payload.test_key, '-',
             payload.case_key]))
        asert_dict.update({'key': key_string, 'round': round_instance, 'dut': dut_instance, 'design': design_instance,
                           "test": test_instance, 'case': case_instance, 'title': payload.name})
        asert_dict.pop("round_key")
        asert_dict.pop("dut_key")
        asert_dict.pop("design_key")
        asert_dict.pop("test_key")
        asert_dict.pop("case_key")
        qs = Problem.objects.create(**asert_dict)
        return qs

    # 更新问题单
    @route.put("/problem/update/{id}", response=ProblemCreateOutSchema,url_name="problem-update")
    @transaction.atomic
    def update_dut(self, id: int, payload: ProblemCreateInputSchema):
        problem_search = Problem.objects.filter(project__id=payload.project_id, ident=payload.ident)
        # 判断是否和同项目同轮次的标识重复
        if len(problem_search) > 1:
            return ChenResponse(code=400, status=400, message='测试需求的标识重复，请检查')
        # 查到当前
        problem_qs = Problem.objects.get(id=id)
        for attr, value in payload.dict().items():
            if attr == 'project_id' or attr == 'round_key' or attr == 'dut_key' or attr == 'design_key' or attr == 'test_key' or attr == 'case_key':
                continue
            if attr == 'name':
                setattr(problem_qs, "title", value)
            setattr(problem_qs, attr, value)
        problem_qs.save()
        return problem_qs

    # 删除问题单
    @route.delete("/problem/delete", url_name="problem-delete")
    @transaction.atomic
    def delete_problem(self, data: DeleteSchema):
        # 根据其中一个id查询出case_id
        problem_single = Problem.objects.filter(id=data.ids[0])[0]
        case_id = problem_single.case.id
        case_key = problem_single.case.key
        multi_delete(data.ids, Problem)
        index = 0
        case_all_qs = Problem.objects.filter(case__id=case_id)
        for single_qs in case_all_qs:
            problem_key = "".join([case_key, '-', str(index)])
            single_qs.key = problem_key
            index = index + 1
            single_qs.save()
        return ChenResponse(message="问题单删除成功！")

    # 单独显示问题单页面需要数据
    @route.get("/getSingleProblem", url_name="problem-single", response=ProblemCreateOutSchema)
    @transaction.atomic
    def search_single_problem(self, data: ProblemSingleInputSchema = Query(...)):
        key_string = "".join(
            [data.round_id, '-', data.dut_id, '-', data.design_id, '-', data.test_id, '-', data.case_id, '-',
             data.problem_id])
        qs = Problem.objects.get(project__id=data.project_id, key=key_string)
        return qs
