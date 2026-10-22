from pathlib import Path
from datetime import date
from typing import List
from shutil import copytree, rmtree
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import Count, Q
from ninja_extra import api_controller, ControllerBase, route
from ninja_extra.permissions import IsAuthenticated
from ninja_jwt.authentication import JWTAuth
from apps.user.models import Users
from utils.chen_pagination import MyPagination
from ninja.pagination import paginate
from ninja.errors import HttpError
from ninja import Query
from utils.chen_response import ChenResponse
from utils.chen_crud import create, multi_delete_project
from apps.project.models import Project, Round, ProjectSoftSummary, StuctSortData, StaticSoftItem, StaticSoftHardware, DynamicSoftTable, \
    DynamicHardwareTable, ProjectDynamicDescription, EvaluateData, EnvAnalysis, CaseStep
from apps.project.schemas.project import ProjectRetrieveSchema, ProjectFilterSchema, ProjectCreateInput, \
    DeleteSchema, SoftSummarySchema, DataSchema, StaticDynamicData, EnvAnalysisSchema
from utils.util import get_str_dict
from apps.project.tools.access_control import (check_project_access, check_project_access_by_id,
                                               ensure_creator_member, check_project_manage)
# 时间处理模块
from apps.project.tool.timeList import time_return_to
# 反射工具
from utils.smallTools.interfaceTools import conditionNoneToBlank

media_path = Path.cwd() / 'media'
base_document_path = Path.cwd() / 'conf/base_document'


def _icontains_or_null(qs, field: str, value: str):
    """
    可空文本字段的模糊检索：值为空时把 NULL 行也算进来。

    项目表的 security_level / report_type / secret 等字段允许为空，
    而 SQL 中 `NULL LIKE '%%'` 结果为 NULL（非真），默认空条件会把未填这些字段的
    项目整条滤掉，表现为"列表空白"。
    """
    if value in (None, ''):
        return qs.filter(Q(**{f'{field}__isnull': True}) | Q(**{f'{field}__icontains': ''}))
    return qs.filter(**{f'{field}__icontains': value})


@api_controller("/testmanage/project", auth=JWTAuth(), permissions=[IsAuthenticated], tags=['项目表相关'])
class ProjectController(ControllerBase):
    @route.get("/index", response=List[ProjectRetrieveSchema])
    @paginate(MyPagination)
    def list_project(self, filters: ProjectFilterSchema = Query(...)):
        conditionNoneToBlank(filters)
        # 处理时间范围：仅当前端**确实传了**区间时才按开始时间过滤。
        # 注意 beginTime 允许为空，而 SQL 里 NULL 落在任何 range 之外，
        # 若默认塞 2000~9999 的区间，未填开始时间的项目会从列表中消失。
        start_time = self.context.request.GET.get('searchOnlyTimeRange[0]')
        end_time = self.context.request.GET.get('searchOnlyTimeRange[1]')
        # 前端返回的member
        member_list = [value for key, value in self.context.request.GET.items() if 'member' in key]
        qs = Project.objects.filter(
            ident__icontains=filters.ident, name__icontains=filters.name,
            duty_person__icontains=filters.duty_person,
            member__contains=member_list).order_by("-create_datetime")
        # step 允许为空：新建项目未填阶段时 NULL 会被 LIKE '%%' 过滤掉，这里补上 NULL 行
        qs = _icontains_or_null(qs, 'step', filters.step)
        if start_time or end_time:
            qs = qs.filter(beginTime__range=[start_time or '2000-01-01', end_time or '9999-01-01'])
        # 下面三个字段同样允许为空：LIKE '%%' 对 NULL 恒为假，会把未填的项目滤掉，
        # 因此空条件时改为"包含 NULL"（用户填了具体值时才真正过滤）
        qs = _icontains_or_null(qs, 'security_level', filters.security_level)
        qs = _icontains_or_null(qs, 'report_type', filters.report_type)
        qs = _icontains_or_null(qs, 'secret', filters.secret)
        # 对软件类型进行处理
        if filters.soft_type != '':
            qs = qs.filter(soft_type=filters.soft_type)

        # ~~role:查询项目的负责人和成员：普通用户只能看到自己参加的项目~~
        # 与详情接口共用同一套 DAC + 密级判定（is_project_accessible），
        # 避免出现"详情能进、列表却看不到"的两套口径
        auth_info: Users = self.context.request.auth
        if auth_info and auth_info.role != 'admin':
            from apps.project.tools.access_control import accessible_projects
            qs = qs.filter(id__in=accessible_projects(auth_info).values('id'))
        return qs

    @route.get("/findOneById/{int:project_id}", response=ProjectRetrieveSchema)
    @transaction.atomic
    def get_project_by_id(self, project_id: int):
        project_obj = get_object_or_404(Project, id=project_id)
        # 自主访问控制：负责人/项目成员/系统管理员方可访问（GB/T 28452 7.1.3）
        check_project_access(project_obj, self.context.request.user)
        return project_obj

    @route.post("/save")
    @transaction.atomic
    def create_project(self, data: ProjectCreateInput):
        data_dict = data.dict()
        if Project.objects.filter(ident=data_dict.get('ident')).exists():
            return ChenResponse(code=400, status=400, message="项目标识重复，请重新设置")
        qs = create(self.context.request, data_dict, Project)
        # 自主访问控制：非管理员创建项目时，把创建人写入负责人/成员（授权起点）
        ensure_creator_member(qs, self.context.request.user)
        # 创建项目时候自动添加第一轮测试
        if qs:
            Round.objects.create(project_id=qs.id, key='0', level='0', title='第1轮测试', name='第1轮测试',
                                 remark='第一轮测试', ident=''.join([qs.ident, '-R1']))
            # 在新增项目时，将/conf/base_document 移动到 /media/{项目ident}/下面
            src_dir = base_document_path
            dist_dir = media_path / qs.ident
            try:
                copytree(src_dir, dist_dir)  # shutil模块直接是复制并命名，如果命名文件存在则抛出FileExists异常
            except PermissionError:
                transaction.set_rollback(True)  # 标记回滚，避免报错但数据已落库
                # 复制中途失败会留下半截目录，清理掉避免下次同 ident 建项目永远 FileExistsError
                rmtree(dist_dir, ignore_errors=True)
                return ChenResponse(code=500, status=500,
                                    message="错误，检查是否打开了服务器的conf中的文档，关闭后重试")
            except FileExistsError:
                transaction.set_rollback(True)
                return ChenResponse(code=409, status=409, message='文件标识已存在或输入为空格，请修改')
            except FileNotFoundError:
                transaction.set_rollback(True)
                return ChenResponse(code=404, status=404, message='文件不存在，请检查')
            return ChenResponse(code=200, status=200, message="添加项目成功，并添加第一轮测试")
        return ChenResponse(code=400, status=400, message="未添加任何项目")

    @route.put("/update/{project_id}")
    @transaction.atomic
    def update_project(self, project_id: int, payload: ProjectCreateInput):
        # 判断标识是否是被允许的字符串
        project = self.get_object_or_exception(Project, id=project_id)
        check_project_manage(project, self.context.request.user)
        old_ident = project.ident
        # 更新操作：只覆盖请求里显式给出的字段，避免前端部分提交时把开始/结束时间等清空
        for attr, value in payload.model_dump(exclude_unset=True).items():
            setattr(project, attr, value)
        project.save()
        new_ident = project.ident
        # 如果新ident不等于老ident，则做 1.更新文件夹名称 2.更新所有轮次中的ident
        if new_ident != old_ident:
            try:
                Path(media_path / old_ident).rename(media_path / project.ident)
                # 同时要更改round和dut的标识
                for r in project.pField.all():
                    r.ident = (r.ident or '').replace(old_ident, new_ident)
                    r.save()
                for d in project.pdField.all():
                    d.ident = (d.ident or '').replace(old_ident, new_ident)
                    d.save()
            except PermissionError:
                transaction.set_rollback(True)  # 标记回滚，避免报错但数据已落库
                return ChenResponse(code=500, status=500, message="错误，请关闭文件资源管理器再试")
            except FileExistsError:
                transaction.set_rollback(True)
                return ChenResponse(code=409, status=409, message='文件标识已存在或输入为空格，请修改')
            except FileNotFoundError:
                transaction.set_rollback(True)
                return ChenResponse(code=404, status=404, message='文件不存在，请检查')
        return ChenResponse(code=200, status=200, message="项目更新成功")

    @route.delete("/delete")
    @transaction.atomic
    def delete(self, data: DeleteSchema):
        # 自主访问控制：仅负责人（或系统管理员）可删除自己的项目
        from apps.project.models import Project as ProjectModel
        for pid in data.ids:
            check_project_manage(get_object_or_404(ProjectModel, id=pid), self.context.request.user)
        idents = multi_delete_project(data.ids, Project)
        # 查询media所属项目文件夹，并删除
        for ident in idents:
            project_media_path = media_path / ident
            try:
                rmtree(project_media_path)
            except FileNotFoundError:
                # 目录本就不存在视为已清理，不应因此回滚已删除的项目数据
                continue
            except PermissionError:
                transaction.set_rollback(True)
                return ChenResponse(status=500, code=500, message='文件被占用，请关闭文件资源管理器后重试')
        return ChenResponse(message="删除成功！")

    # 看板页面接口
    @route.get('/board')
    @transaction.atomic
    def board(self, id: int):
        project_obj = get_object_or_404(Project, id=id)
        check_project_access(project_obj, self.context.request.user)
        # 1.项目阶段直接转字符串
        step_str = get_str_dict(project_obj.step, 'step')
        # 2.返回时间信息
        # 3.返回人员信息
        # 4.返回研制方信息
        # 5.返回用例信息
        case_ids = list(project_obj.pcField.values_list('id', flat=True))
        exe_count = 0  # 已执行数量
        noexe_count = 0  # 未执行数量
        partexe_count = 0  # 部分执行数量
        ## 5.1 计算已执行的用例数 -> 所以的都通过/未通过才算执行，否则部分执行
        # 一次性按用例聚合步骤通过情况，避免逐用例多次 count 查询（N+1）
        # 注意：注解名不能与模型字段 passed 同名，否则 Q(passed=...) 会错误地指向注解
        step_stats = {
            row['case_id']: row
            for row in CaseStep.objects.filter(case__project=project_obj).values('case_id').annotate(
                total_cnt=Count('id'),
                passed_cnt=Count('id', filter=Q(passed='1')),
                notpassed_cnt=Count('id', filter=Q(passed='2')),
            )
        }
        for case_id in case_ids:
            stat = step_stats.get(case_id)
            steps_count = stat['total_cnt'] if stat else 0  # 步骤总数
            passed_steps_count = stat['passed_cnt'] if stat else 0
            notPassed_steps_count = stat['notpassed_cnt'] if stat else 0
            notExe_steps_count = steps_count - passed_steps_count - notPassed_steps_count
            if notExe_steps_count > 0:
                # 步骤全是未执行，则用例未执行
                if notExe_steps_count == steps_count:
                    noexe_count += 1
                else:
                    partexe_count += 1
            else:
                exe_count += 1

        # 6.计算问题单数
        problem_status_list = list(project_obj.projField.values_list('status', flat=True))
        close_count = sum(1 for status in problem_status_list if status == '1')
        open_count = len(problem_status_list) - close_count

        # 7.将时间提取 todo:后续将计算的事件放入该页面
        timers = {'round_time': []}
        rounds = project_obj.pField.all()
        timers['start_time'] = project_obj.beginTime  # type:ignore
        timers['end_time'] = project_obj.endTime  # type:ignore
        for round in rounds:
            round_number = int(round.key) + 1
            timers['round_time'].append({
                'name': f'第{round_number}轮次',
                'start': round.beginTime,
                'end': round.endTime
            })

        # 8.提取所有需求下面测试项、用例数量
        # 9.提取测试类型下面测试项数量、用例数量
        data_list = []
        for round in rounds:
            round_dict = {'name': f'第{int(round.key) + 1}轮次', 'desings': [], 'method_demand': {},
                          'method_case': {}}
            # 预取测试项/用例，用 len 取代逐条 count（避免 N+1）
            designs = round.dsField.prefetch_related('dtField', 'dcField')
            for design in designs:
                design_dict = {
                    'name': design.name,
                    'demand_count': len(design.dtField.all()),
                    'case_count': len(design.dcField.all())
                }
                round_dict['desings'].append(design_dict)
            demands = round.rtField.all()
            for demand in demands:
                test_type = get_str_dict(demand.testType, 'testType')
                if test_type not in round_dict['method_demand']:
                    round_dict['method_demand'][test_type] = 1
                else:
                    round_dict['method_demand'][test_type] += 1
            cases = round.rcField.select_related('test').all()
            for case in cases:
                testDemand = case.test
                case_type = get_str_dict(testDemand.testType, 'testType')
                if case_type not in round_dict['method_case']:
                    round_dict['method_case'][case_type] = 1
                else:
                    round_dict['method_case'][case_type] += 1
            data_list.append(round_dict)

        return {
            'ident': project_obj.ident,
            'name': project_obj.name,
            'step': step_str,
            'title_info': {
                '时间': {
                    '开始时间': project_obj.beginTime,
                    '结束时间': project_obj.endTime,
                    '到现在时间': f"{(date.today() - project_obj.beginTime).days}天" if project_obj.beginTime else '',
                },
                '人员': {
                    '负责人': project_obj.duty_person,
                    '成员数': len(project_obj.member or []),
                },
                '开发方信息': {
                    '联系人': project_obj.dev_contact,
                    '电话': project_obj.dev_contact_phone,
                    '邮箱': project_obj.dev_email
                },
                '用例数': {
                    '总数': len(case_ids),
                    '已执行': exe_count,
                    '未执行': noexe_count,
                    '部分执行': partexe_count,
                },
                '问题数': {
                    '总数': len(problem_status_list),
                    '已闭环': close_count,
                    '未闭环': open_count,
                }
            },
            'time_line': timers,
            'statistics': data_list,
        }

    # 看板页面的生成文档时间接口
    @route.get('/document_time_show')
    @transaction.atomic
    def document_time_show(self, id: int):
        check_project_access_by_id(id, self.context.request.user)
        time = time_return_to(id)
        return time

    # [变] 项目级信息前端告警数据获取
    @route.get("/project_info_status/")
    @transaction.atomic
    def project_info_status(self, id: int):
        project_obj = self.get_project_by_id(id)

        # 统一配置每个状态的检查逻辑
        status_configs = {
            "soft_summary": {
                "model": ProjectSoftSummary,
                "check": lambda qs: qs.exists() and qs.first().data_schemas.exists()
            },
            "interface_image": {
                "model": StuctSortData,
                "check": lambda qs: qs.exists()
            },
            "static_soft_item": {
                "model": StaticSoftItem,
                "check": lambda qs: qs.exists()
            },
            "static_soft_hardware": {
                "model": StaticSoftHardware,
                "check": lambda qs: qs.exists()
            },
            "dynamic_soft_item": {
                "model": DynamicSoftTable,
                "check": lambda qs: qs.exists()
            },
            "dynamic_soft_hardware": {
                "model": DynamicHardwareTable,
                "check": lambda qs: qs.exists()
            },
            "dynamic_des": {
                "model": ProjectDynamicDescription,
                "check": lambda qs: qs.exists() and qs.first().data_schemas.exists()
            },
            "evaluate_data": {
                "model": EvaluateData,
                "check": lambda qs: qs.exists()
            },
            "env_analysis": {
                "model": EnvAnalysis,
                "check": lambda qs: qs.exists()
            }
        }

        all_status = {}
        for status_key, config in status_configs.items():
            qs = config["model"].objects.filter(project=project_obj)
            all_status[status_key] = config["check"](qs)
        return ChenResponse(status=200, code=20000, data=all_status, message='查询成功')

    # [变] 封装结构化数据新增-修改（针对project - OneToOne - DataSchemas形式）
    @classmethod
    def bulk_create_data_schemas(cls, parent_obj, datas: list[DataSchema]):
        """
            批量创建结构化排序数据 (自动类型推断)
            Args:
                parent_obj: 父级对象，可以是 ProjectSoftSummary 或 Project 的实例
                datas (list[DataSchema]): 数据模式对象列表
        """
        # 动态确定所属父model
        field_name = None  # type:ignore
        if isinstance(parent_obj, ProjectSoftSummary):
            field_name = 'soft_summary'
        elif isinstance(parent_obj, Project):
            field_name = 'project'
        elif isinstance(parent_obj, ProjectDynamicDescription):
            field_name = 'dynamic_description'
        else:
            raise HttpError(400, "添加的数据未在系统内，请联系管理员")

        data_list = []
        for data in datas:
            new_data = StuctSortData(
                type=data.type,
                fontnote=data.fontnote,
                content=data.content,
            )
            setattr(new_data, field_name, parent_obj)
            data_list.append(new_data)
        StuctSortData.objects.bulk_create(data_list)

    # 封装只有model不同 -修改和新增dataSchemas（针对project - OneToOne - DataSchemas形式）
    @classmethod
    def create_or_modify_data_schemas(cls, id: int, model, data):
        project_obj = get_object_or_404(Project, pk=id)
        qs = model.objects.filter(project=project_obj)
        if qs.exists():
            obj = qs.first()
            # 如果存在则修改：先删除再创建
            obj.data_schemas.all().delete()
            cls.bulk_create_data_schemas(obj, data)
        else:
            parent_obj = model.objects.create(project=project_obj)
            cls.bulk_create_data_schemas(parent_obj, data)

    # ~~~软件概述-新增和修改~~~
    @route.post('/soft_summary/')
    @transaction.atomic
    def soft_summary(self, payload: SoftSummarySchema):
        self.create_or_modify_data_schemas(payload.id, ProjectSoftSummary, payload.data)

    # ~~~动态环境描述-新增和修改~~~
    @route.post('/dynamic_description/')
    @transaction.atomic
    def dynamic_description(self, payload: SoftSummarySchema):
        self.create_or_modify_data_schemas(payload.id, ProjectDynamicDescription, payload.data)

    @classmethod
    def get_res_from_info(cls, project_obj: Project, model) -> list[dict] | None:
        """model: 当前一对一模型，直接获取结构化数据信息数组返回"""
        qs = model.objects.filter(project=project_obj)
        if qs.exists():
            obj = qs.first()
            ds_qs = obj.data_schemas.all()
            data_list = [{
                "type": item.type,
                "content": item.content,
                "fontnote": item.fontnote,
            } for item in ds_qs]
            return data_list
        return None

    # ~~~软件概述-获取到前端展示~~~
    @route.get("/get_soft_summary/", response=list[DataSchema])
    @transaction.atomic
    def get_soft_summary(self, id: int):
        project_obj = self.get_project_by_id(id)
        data_list = self.get_res_from_info(project_obj, ProjectSoftSummary)
        if data_list:
            return ChenResponse(status=200, code=20000, data=data_list)
        return ChenResponse(status=200, code=20000, data=[])

    # ~~~动态环境描述 - 获取展示~~~
    @route.get("/dynamic_des/", response=list[DataSchema])
    @transaction.atomic
    def get_dynamic_des(self, id: int):
        project_obj = self.get_project_by_id(id)
        data_list = self.get_res_from_info(project_obj, ProjectDynamicDescription)
        if data_list:
            return ChenResponse(status=200, code=20000, data=data_list)
        return ChenResponse(status=200, code=20000, data=[])

    # ~~~接口图新增或修改~~~
    @route.post("/interface_image/")
    @transaction.atomic
    def post_interface_image(self, id: int, dataSchema: DataSchema):
        project_obj = self.get_project_by_id(id)
        image_qs = StuctSortData.objects.filter(project=project_obj)
        if image_qs.exists():
            image_qs.delete()
        self.bulk_create_data_schemas(project_obj, [dataSchema])

    # ~~~接口图-获取数据~~~
    @route.get("/get_interface_image/", response=DataSchema)
    @transaction.atomic
    def get_interface_image(self, id: int):
        project_obj = self.get_project_by_id(id)
        image_qs = StuctSortData.objects.filter(project=project_obj)
        if image_qs.exists():
            # 如果存在则返回数据
            image_obj = image_qs.first()
            return ChenResponse(status=200, code=25001, data={
                "type": image_obj.type,
                "content": image_obj.content,
                "fontnote": image_obj.fontnote,
            })
        return ChenResponse(status=200, code=25002, data=None)

    # 动态返回是哪个模型
    @classmethod
    def get_model_from_category(cls, category: str):
        mapDict = {
            '静态软件项': StaticSoftItem,
            '静态硬件项': StaticSoftHardware,
            '动态软件项': DynamicSoftTable,
            '动态硬件项': DynamicHardwareTable,
            '测评数据': EvaluateData
        }
        model = mapDict.get(category)
        if model is None:
            raise HttpError(400, f'不支持的类别：{category}')
        return model

    # ~~~静态软件项、静态硬件项、动态软件项、动态硬件项 - 获取~~~
    @route.get("/get_static_dynamic_items/")
    def get_static_dynamic_items(self, id: int, category: str):
        project_obj = self.get_project_by_id(id)
        item_qs = self.get_model_from_category(category).objects.filter(project=project_obj)
        if item_qs.exists():
            item_obj = item_qs.first()
            if item_obj:
                return ChenResponse(status=200, code=25001, data={
                    "table": item_obj.table,
                    "fontnote": item_obj.fontnote,
                    "rounds": item_obj.rounds_map or []
                })
        return ChenResponse(status=200, code=25002, data=None)

    # ~~~静态软件项、静态硬件项、动态软件项、动态硬件项、测评数据 - 新增或修改~~~
    @route.post("/post_static_dynamic_item/")
    @transaction.atomic
    def post_static_dynamic_item(self, data: StaticDynamicData):
        project_obj = self.get_project_by_id(data.id)
        model = self.get_model_from_category(data.category)
        item_qs = model.objects.filter(project=project_obj)
        # 处理rounds_map
        rounds = data.rounds
        if rounds is None:
            rounds = [["0"]] * len(data.table)

        if item_qs.exists():
            # 如果存在则修改
            item_qs.delete()
        model.objects.create(
            project=project_obj,
            table=data.table,
            fontnote=data.fontnote,
            rounds_map=rounds,
        )
        return ChenResponse(status=200, code=20000, message="保存成功")

    # ~~~环境差异性分析 - 获取~~~
    @route.get("/get_env_analysis/")
    @transaction.atomic
    def get_env_analysis(self, id: int):
        project_obj = self.get_project_by_id(id)
        qs = EnvAnalysis.objects.filter(project=project_obj)
        if qs.exists():
            obj = qs.first()
            return ChenResponse(status=200, code=25001, data={"table": obj.table, "fontnote": obj.fontnote, "description": obj.description})
        return ChenResponse(status=200, code=25002, data=None)

    # ~~~环境差异性分析 - 新增和修改~~~
    @route.post("/post_env_analysis/")
    @transaction.atomic
    def post_env_analysis(self, data: EnvAnalysisSchema):
        project_obj = self.get_project_by_id(data.id)
        qs = EnvAnalysis.objects.filter(project=project_obj)
        if qs.exists():
            qs.delete()
        EnvAnalysis.objects.create(project=project_obj, table=data.table, fontnote=data.fontnote, description=data.description)
