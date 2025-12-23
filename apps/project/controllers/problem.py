import datetime
import numpy as np
from ninja_extra import api_controller, ControllerBase, route
from ninja import Query
from ninja_jwt.authentication import JWTAuth
from ninja_extra.permissions import IsAuthenticated
from ninja.pagination import paginate
from apps.dict.models import DictItem
from utils.chen_pagination import MyPagination
from django.db import transaction
from typing import List, Optional
from utils.chen_response import ChenResponse
from utils.codes import HTTP_INDEX_ERROR
from django.shortcuts import get_object_or_404
from apps.project.models import Case, Problem, Project, TestDemand
from apps.project.schemas.problem import (
    DeleteSchema,
    ProblemModelOutSchema,
    ProblemFilterSchema,
    ProblemCreateOutSchema,
    ProblemCreateInputSchema,
    ProblemSingleInputSchema,
    ProblemUpdateInputSchema,
    ProblemFilterWithHangSchema
)
from utils.util import get_str_abbr
from utils.smallTools.interfaceTools import conditionNoneToBlank

@api_controller("/project", auth=JWTAuth(), permissions=[IsAuthenticated], tags=['问题单系列'])
class ProblemController(ControllerBase):
    @route.get("/getProblemList", response=List[ProblemModelOutSchema], exclude_none=True,
               url_name="problem-list")
    @transaction.atomic
    @paginate(MyPagination)
    def get_problem_list(self, data: ProblemFilterSchema = Query(...)):
        project_id = data.project_id
        conditionNoneToBlank(data)
        # 组装查询条件
        query_params = {
            "project__id":data.project_id,
            "ident__icontains":data.ident,
            "name__icontains":data.name,
            "status__icontains":data.status,
            "type__icontains":data.type,
            "grade__icontains":data.grade,
            "operation__icontains":data.operation,
            "postPerson__icontains":data.postPerson
        }
        # 如果没有多个key传递则是汇总界面
        if data.dut_id and data.design_id and data.test_id and data.case_id:
            case_key = "".join(
                [data.round_id, '-', data.dut_id, '-', data.design_id, '-', data.test_id, '-', data.case_id])
            query_params['case__key'] = case_key
        else:
            query_params['case__round__key'] = data.round_id
        qs = Problem.objects.filter(**query_params).order_by("id")

        # 遍历通过代码不通过ORM查询闭环方式-巧妙使用numpy中array对象的in方法来判断
        closeMethod1 = self.context.request.GET.get("closeMethod[0]")
        closeMethod2 = self.context.request.GET.get("closeMethod[1]")
        query_add_closeMethod = []
        for query in qs:
            arr = np.array(query.closeMethod)
            if closeMethod1 is None and closeMethod2 is None:
                query_add_closeMethod.append(query)
                continue
            if closeMethod1 in arr:
                query_add_closeMethod.append(query)
                continue
            if closeMethod2 in arr:
                query_add_closeMethod.append(query)
                continue
        return query_add_closeMethod

    # 搜索全部问题单/或查询轮次下的问题单
    @route.get('/problem/searchAllProblem', response=List[ProblemModelOutSchema], exclude_none=True,
               url_name="problem-allList")
    @transaction.atomic
    @paginate(MyPagination)
    def get_all_problems(self, round_key: Optional[str] = False, data: ProblemFilterWithHangSchema = Query(...)):
        project_id = data.project_id
        conditionNoneToBlank(data)
        # 先查询当前项目
        qs = Problem.objects.filter(project__id=data.project_id,
                                    ident__icontains=data.ident,
                                    name__icontains=data.name,
                                    status__icontains=data.status,
                                    type__icontains=data.type,
                                    grade__icontains=data.grade,
                                    operation__icontains=data.operation,
                                    postPerson__icontains=data.postPerson,
                                    ).order_by("id")
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
        # 遍历所有problem，查询是有否有关联case，如果有则设置hang为True，否则False
        hang = True
        # 过滤不是该轮次的问题单对象列表
        deleted_problem_list = []
        for pro_obj in query_final:
            case_exists = pro_obj.case.exists()
            if not case_exists:
                setattr(pro_obj, "hang", hang)
            # 如果有关联用例还要看是否是查询轮次的问题单，过滤出去
            elif case_exists:
                hang = False
                setattr(pro_obj, "hang", hang)
                hang = True
                if round_key:
                    if not pro_obj.case.filter(round__key=round_key).exists():
                        deleted_problem_list.append(pro_obj)
        for dq in deleted_problem_list:
            query_final.remove(dq)
        # !!!如果是轮次查询则返回轮次，如果是关联查询则查询关联当前的case
        if round_key:
            pass
        else:
            case_obj = Case.objects.filter(project_id=project_id, key=data.key).first()
            if case_obj:
                for pro_obj in query_final:
                    # 查询关联的case
                    related = False
                    for re_case in pro_obj.case.all():
                        if case_obj.id == re_case.id:
                            related = True
                    setattr(pro_obj, "related", related)
        # 过滤查询悬挂逻辑
        query_last = []
        if data.hang == '3' or data.hang == '':  # 疑问：为什么会是空字符串
            query_last = query_final
        if data.hang == '2':
            for pp in query_final:
                if not pp.hang:
                    query_last.append(pp)
        if data.hang == '1':
            for pp in query_final:
                if pp.hang is True:
                    query_last.append(pp)
        return query_last

    @staticmethod
    def __date_solve(payload: ProblemCreateInputSchema):
        """辅助函数：
        1.设置问题单时间，而不是默认进入时间，传入schema对象，返回schema对象，只对里面时间进行处理
        """
        project_obj = get_object_or_404(Project, id=payload.project_id)
        round_obj = project_obj.pField.filter(key=payload.round_key).first()
        if round_obj:
            if payload.postDate is None:
                payload.postDate = round_obj.beginTime + datetime.timedelta(days=1)
            if payload.designDate is None:
                payload.designDate = round_obj.beginTime + datetime.timedelta(days=2)
        return payload

    # 添加问题单
    @route.post("/problem/save", response=ProblemCreateOutSchema, url_name="problem-create")
    @transaction.atomic
    def create_case_demand(self, payload: ProblemCreateInputSchema):
        payload = self.__date_solve(payload)
        asert_dict = payload.dict()
        project_id = payload.project_id
        # 查询problem的总数
        problem_count = Problem.objects.filter(project_id=project_id).count()
        # 查询当前各个前面节点的instance
        pop_keys: List[str] = ["round_key", "dut_key", "design_key", "test_key", "case_key"]
        for pkey in pop_keys:
            asert_dict.pop(pkey)
        # 处理问题单标识PT_项目ident_数目依次增加
        asert_dict["ident"] = str(problem_count + 1)
        qs = Problem.objects.create(**asert_dict)
        # 处理时间
        qs.postDate = payload.postDate
        qs.designDate = payload.designDate
        qs.save()
        # 分两个逻辑处理，无关联创建问题单/case下面创建问题单
        if payload.case_key:
            # 构造case_key
            case_key = "".join(
                [payload.round_key, "-", payload.dut_key, '-', payload.design_key, '-', payload.test_key, '-',
                 payload.case_key])
            # 查询出所属的case
            case_obj = Case.objects.filter(project_id=project_id, key=case_key).first()
            qs.case.add(case_obj)
            qs.save()
        # 对problem的ident排序
        self.reset_problem_ident(project_id)
        return qs

    # 更新问题单
    @route.put("/problem/update/{id}", response=ProblemCreateOutSchema, url_name="problem-update")
    @transaction.atomic
    def update_problem(self, id: int, payload: ProblemCreateInputSchema):
        # 查到当前
        problem_qs = Problem.objects.get(id=id)
        for attr, value in payload.dict().items():
            setattr(problem_qs, attr, value)
        problem_qs.save()
        return ChenResponse(message="问题单更新成功")

    # 弹窗的-更新问题单
    @route.put("/problem/modalupdate/{id}", response=ProblemCreateOutSchema, url_name="problem-update")
    @transaction.atomic
    def update_modal_problem(self, id: int, payload: ProblemUpdateInputSchema):
        # 查到当前
        problem_qs = Problem.objects.get(id=id)
        for attr, value in payload.dict().items():
            setattr(problem_qs, attr, value)
        problem_qs.save()
        return ChenResponse(message="问题单更新成功")

    # 删除问题单
    @route.delete("/problem/delete", url_name="problem-delete")
    @transaction.atomic
    def delete_problem(self, data: DeleteSchema):
        # 1.查询出所有被删除id
        problems = Problem.objects.filter(id__in=data.ids)
        if not problems.exists():
            return ChenResponse(status=500, code=HTTP_INDEX_ERROR, message='您未选取删除内容')
        # 4.查询出当前项目id
        project_id = None
        # 2.循环该取出problem
        for problem in problems:
            project_id = problem.project_id
            # 3. 直接删除case关联，然后删除自己
            problem.case.clear()
            problem.delete()
        # 4.找到对应项目的所有problems进行排序
        if project_id is not None:
            self.reset_problem_ident(project_id)
        return ChenResponse(message="问题单删除成功！")

    # 根据问题单id，返回关联的用例s
    @route.get('/getRelativeCases', url_name='problem-relative-case')
    @transaction.atomic
    def get_relative_cases(self, id: int):
        problem_qs = get_object_or_404(Problem, id=id)
        cases = problem_qs.case.all()
        case_list = []
        for case in cases:
            case_dict = {
                'id': case.id,
                'case': case.title,
                'round': case.round.title,
                'dut': case.dut.title,
                'design': case.design.title,
            }
            demand = case.test
            case_dict['demand'] = demand.title
            demand_testType_showtitle = get_str_abbr(demand.testType, 'testType')
            case_dict['demand_ident'] = "-".join(['XQ', demand_testType_showtitle, demand.ident])
            case_list.append(case_dict)
        return case_list

    # 单独显示问题单页面需要数据
    @route.get("/getSingleProblem", url_name="problem-single", response=ProblemCreateOutSchema)
    @transaction.atomic
    def search_single_problem(self, data: ProblemSingleInputSchema = Query(...)):
        key_string = "".join(
            [data.round_id, '-', data.dut_id, '-', data.design_id, '-', data.test_id, '-', data.case_id, '-',
             data.problem_id])
        qs = Problem.objects.get(project__id=data.project_id, key=key_string)
        return qs

    # 让测试用例关联/取消问题单
    @route.get('/problem/relateProblem', exclude_none=True, url_name="problem-allList")
    @transaction.atomic
    def relate_problem(self, case_key: str, problem_id: int, val: bool):  # val是将要变成的值
        # 先判断将要变成的值是否为True
        problem_obj: Problem = Problem.objects.filter(id=problem_id).first()
        project_id = problem_obj.project_id  # 根据问题单反推项目id
        case_obj = Case.objects.filter(project_id=project_id, key=case_key).first()
        flag = False  # 是否操作成功的标志
        if val:
            # 这分支是进行关联操作
            # 5月15日新需求：一个用例只能关联一个问题单
            if case_obj.caseField.count() >= 1:
                return ChenResponse(code=400, status=400, message='请注意：一个用例只允许关联一个问题单',
                                    data={'isOK': False})
            case_obj.caseField.add(problem_obj)
            flag = True
        else:
            case_obj.caseField.remove(problem_obj)
            flag = True
        # 排序ident
        if project_id:
            self.reset_problem_ident(project_id)
        return ChenResponse(code=200, status=200, message='关联或取消关联成功...',
                            data={'isOK': flag, 'key': case_obj.key})

    # 类方法：操作后对problem的ident排序：先基于轮次排序，然后基于测试项类型排序
    @classmethod
    def reset_problem_ident(cls, project_id: int):
        project_obj: Project = get_object_or_404(Project, id=project_id)
        # 获取所有问题单
        problem_qs = project_obj.projField.prefetch_related('case').prefetch_related('case__test')
        # 待排序列表
        not_sorted_problems = []
        # 处理为List[Dict]以便后续排序修改ident
        for problem in problem_qs:
            cases = problem.case.all()
            if len(cases):
                # 如果关联了case
                belong_demand: TestDemand = cases[0].test
                # 找到对应测试类型
                test_type = DictItem.objects.get(dict__code='testType', key=belong_demand.testType)
                # 找到测试类型的sort/找到轮次key
                not_sorted_problems.append({
                    'problem': problem,
                    'sort': test_type.sort,
                    'round_key': belong_demand.round.key,
                })
            else:
                # 如果没有关联case
                not_sorted_problems.append({
                    'problem': problem,
                    'sort': 1024,
                    'round_key': 1024,
                })
        # 排序后修改ident
        round_sorted_problems = sorted(not_sorted_problems, key=lambda x: int(x['round_key']))
        last_sorted_problems = sorted(round_sorted_problems, key=lambda x: int(x['sort']))
        # 根据排序修改problem的ident
        for index, problem_dict in enumerate(last_sorted_problems):
            problem_dict['problem'].ident = str(index + 1)
            problem_dict['problem'].save()
