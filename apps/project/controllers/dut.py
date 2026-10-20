import os
import tempfile
from ninja_extra import api_controller, ControllerBase, route
from ninja import Query, File, UploadedFile
from ninja.errors import HttpError
from ninja_jwt.authentication import JWTAuth
from ninja_extra.permissions import IsAuthenticated
from ninja.pagination import paginate
from utils.chen_pagination import MyPagination
from django.db import transaction
from typing import List
from utils.chen_response import ChenResponse
from utils.chen_crud import multi_delete_dut
from utils.codes import HTTP_INDEX_ERROR
from apps.project.models import Dut, Round, Project, DutMetrics
from django.shortcuts import get_object_or_404
# 自主访问控制（GB/T 28452-2012 7.1.3）
from apps.project.tools.access_control import (check_project_access, check_project_access_by_id,
                                               check_objects_access, get_object_in_project)
from apps.project.schemas.dut import DutModelOutSchema, DutFilterSchema, DutTreeReturnSchema, DutTreeInputSchema, \
    DutCreateInputSchema, DutCreateOutSchema, DeleteSchema, DutCreateR1SoDutSchema
# 导入自动生成design、demand、case的辅助函数
from apps.project.tools.auto_create_data import auto_create_jt_and_dm, auto_create_wd
from apps.project.tools.delete_change_key import dut_delete_sub_node_key
from utils.smallTools.interfaceTools import model_retrieve
# 导入代码统计函数
from apps.project.tool.source_counter import analyze_code_directory, extract_and_get_paths
# 导入需求解析类
from apps.project.tool.xq_parse import DocxChapterExtractor

@api_controller("/project", auth=JWTAuth(), permissions=[IsAuthenticated], tags=['被测件数据'])
class DutController(ControllerBase):
    @route.get("/getDutList", response=List[DutModelOutSchema], exclude_none=True, url_name="dut-list")
    @transaction.atomic
    @paginate(MyPagination)
    def get_dut_list(self, filters: DutFilterSchema = Query(...)):
        check_project_access_by_id(filters.project_id, self.context.request.user)
        qs = model_retrieve(filters, Dut.objects, ['project_id', 'round_id']).order_by("-create_datetime")
        qs = qs.filter(project__id=filters.project_id, round__key=filters.round_id)
        return qs

    # 处理树状数据
    @route.get("/getDutInfo", response=List[DutTreeReturnSchema], url_name="dut-info")
    def get_round_tree(self, payload: DutTreeInputSchema = Query(...)):
        check_project_access_by_id(payload.project_id, self.context.request.user)
        qs = Dut.objects.filter(project__id=payload.project_id, round__key=payload.key)
        return qs

    # 获取单个dut-根据项目id和dut.key
    @route.get("/getDutOne", response=DutModelOutSchema, url_name="dut-one")
    @transaction.atomic
    def get_dut(self, project_id: int, key: str):
        check_project_access_by_id(project_id, self.context.request.user)
        dut_qs = Dut.objects.filter(project_id=project_id, key=key).first()
        if dut_qs:
            return dut_qs
        raise HttpError(404, "未找到相应的数据")

    @route.get("/getDutOneById", response=DutModelOutSchema, url_name='dut-one-by-id')
    def get_one_by_id(self, id: int):
        dut_qs = Dut.objects.filter(id=id).first()
        if dut_qs:
            check_project_access(dut_qs.project, self.context.request.user)
            return dut_qs
        raise HttpError(404, "未找到相应的数据")

    # 添加被测件
    @route.post("/dut/save", url_name="dut-create", response=DutCreateOutSchema)
    @transaction.atomic
    def create_dut(self, payload: DutCreateInputSchema):
        check_project_access_by_id(payload.project_id, self.context.request.user)
        asert_dict = payload.dict(exclude_none=True)
        # 归属轮次/标识缺失时明确报 400，避免拼 key 时 NoneType 导致 500
        if not payload.round_key:
            raise HttpError(400, '缺少归属轮次参数，请刷新页面后重试')
        if not payload.ident:
            raise HttpError(400, '被测件标识不能为空')
        # 当被测件为SO时，一个轮次只运行有一个
        if payload.type == 'SO':
            if Dut.objects.filter(project__id=payload.project_id, round__key=payload.round_key, type='SO').exists():
                return ChenResponse(code=400, status=400, message='源代码被测件一个轮次只能添加一个')
        # 判重标识
        if Dut.objects.filter(project__id=payload.project_id, round__key=payload.round_key,
                              ident=payload.ident).exists():
            return ChenResponse(code=400, status=400, message='被测件的标识重复，请检查')
        # 查询当前key应该为多少（先锁住轮次行，串行分配被测件 key，避免并发 count 冲突）
        Round.objects.select_for_update().filter(project__id=payload.project_id, key=payload.round_key).first()
        dut_count = Dut.objects.filter(project__id=payload.project_id, round__key=payload.round_key).count()
        key_string = ''.join([payload.round_key, "-", str(dut_count)])
        # 然后在标识后面加上UT+KEY -> 注意删除时也改了key要对应修改blink1->>>>>>
        asert_dict['ident'] = ''.join([asert_dict['ident'], str(dut_count + 1)])
        # 查询当前的round_id（key 不合法时返回 404 而非 500）
        round_instance = get_object_or_404(Round, project__id=payload.project_id, key=payload.round_key)
        asert_dict.update({'key': key_string, 'round': round_instance, 'title': payload.name})
        asert_dict.pop("round_key")
        qs = Dut.objects.create(**asert_dict)
        return qs

    # 更新被测件
    @route.put("/dut/update/{id}", url_name="dut-update", response=DutCreateOutSchema)
    @transaction.atomic
    def update_dut(self, id: int, payload: DutCreateInputSchema):
        # 目标被测件必须属于 payload 指定的项目
        dut_qs = get_object_in_project(Dut, id, payload.project_id, self.context.request.user)
        dut_search = Dut.objects.filter(project__id=payload.project_id, round__key=payload.round_key,
                                        ident=payload.ident).exclude(id=id)
        # 判断是否和同项目同轮次的标识重复（排除自身；空标识不校验）
        if payload.ident and dut_search.exists():
            return ChenResponse(code=400, status=400, message='被测件的标识重复，请检查')
        # 两个分支（SO / 非SO）逻辑一致，仅非源代码被测件需清空代码统计字段，这里合并处理
        for attr, value in payload.dict().items():
            if attr == 'project_id' or attr == 'round_key':
                continue
            # 非源代码被测件：清空代码统计字段（由上传的源代码分析重新填充）
            if payload.type != 'SO' and attr in ('total_lines', 'effective_lines', 'comment_lines'):
                setattr(dut_qs, attr, "")
                continue
            if attr == 'name':
                setattr(dut_qs, "title", value)
            setattr(dut_qs, attr, value)
        dut_qs.save()
        return dut_qs

    # 删除被测件 - 1.重新对key排序 2.重新对表示尾号排序
    @route.delete("/dut/delete", url_name="dut-delete")
    @transaction.atomic
    def delete_dut(self, data: DeleteSchema):
        # 逐个校验每条选中被测件的项目归属（防止只校验第一行、其余行跨项目删除）
        dut_objs = check_objects_access(Dut, data.ids, self.context.request.user)
        # 源代码类被测件不可删除
        so_ids = {obj.id for obj in dut_objs if obj.type == 'SO'}
        message = '源代码被测件不能删除' if so_ids else '被测件删除成功'
        deletable = [obj for obj in dut_objs if obj.id not in so_ids]
        affected = {(obj.round_id, obj.round.key) for obj in deletable}
        multi_delete_dut([obj.id for obj in deletable], Dut)
        # 每个受影响的轮次都重排 key 与 ident 尾号
        for round_id, round_key in affected:
            dut_all_qs = Dut.objects.filter(round__id=round_id).order_by('id')
            if not dut_all_qs.exists():
                continue
            ident_before_string = dut_all_qs[0].ident.split("UT")[0]  # 输出类似于“R2233-R1-”
            index = 0
            for single_qs in dut_all_qs:
                single_qs.key = "".join([round_key, '-', str(index)])
                single_qs.ident = ident_before_string + "UT" + str(index + 1)
                index = index + 1
                single_qs.save()
                # 不仅重排自己的还要改所有子类的key，因为还是之前的key
                dut_delete_sub_node_key(single_qs)

        return ChenResponse(message=message)

    # 查询项目中第一轮次是否存在源代码的被测件 -> 5月16日更改：查每一轮是否有源代码被测件
    @route.get("/dut/soExist", url_name="dut-soExist")
    @transaction.atomic
    def delete_soExist(self, id: int):
        project_obj = get_object_or_404(Project, id=id)
        # 先查询项目的所有轮次
        round_qs = project_obj.pField.all()
        data = {
            'round_count': round_qs.count(),
            'round_list': []
        }
        for round_obj in round_qs:
            so_dut_exists = round_obj.rdField.filter(type='SO').exists()
            round_dict = {
                'key': round_obj.key,
                'isExists': so_dut_exists
            }
            data['round_list'].append(round_dict)
        return ChenResponse(code=200, status=200, message='在data展示轮次是否有源代码信息', data=data)

    # 弹窗添加第一轮被测件源代码信息，另外创建测试项（静态分析、代码审查），测试用例（静态分析、代码审查）
    @route.post("/dut/createR1Sodut", response=DutCreateOutSchema, url_name='dut-r1SoDut')
    @transaction.atomic
    def create_r1_so_dut(self, data: DutCreateR1SoDutSchema):
        check_project_access_by_id(data.project_id, self.context.request.user)
        asert_dict = data.dict(exclude_none=True)  # asert_dict['round_key']可以获取是第几轮次
        round_key = asert_dict.pop('round_key')
        project_obj = get_object_or_404(Project, id=data.project_id)
        if Dut.objects.filter(project__id=data.project_id, round__key=round_key, type='SO').exists():
            return ChenResponse(code=400, status=400, message='源代码被测件一个轮次只能添加一个')
        # 查询当前key应该为多少
        dut_count = Dut.objects.filter(project__id=data.project_id, round__key=round_key).count()
        key_string = ''.join([round_key, "-", str(dut_count)])
        asert_dict['ident'] = "-".join(
            [project_obj.ident, ''.join(['R', str(int(round_key) + 1)]), 'UT', str(dut_count + 1)]).replace("UT-", "UT")
        # 查询round_id
        round_obj = project_obj.pField.filter(key=round_key).first()
        if not round_obj:
            return ChenResponse(code=400, status=400, message='轮次不存在，请检查...')
        round_id = round_obj.id
        asert_dict['round_id'] = round_id
        asert_dict.update({'key': key_string, 'title': '软件源代码', 'type': 'SO', 'name': '软件源代码', 'level': '1'})
        dut_qs: Dut = Dut.objects.create(**asert_dict)
        # 到这里就自动生成了第一轮的源代码dut，下面使用辅助函数自动生成（静态分析、代码审查）
        user_name = self.context.request.user.name
        # 注意判断如果非第一轮次
        # 1.自动生成静态分析、代码审查
        auto_create_jt_and_dm(user_name, dut_qs, project_obj)
        # 2.自动生成文档审查在源代码被测件中
        auto_create_wd(user_name, dut_qs, project_obj)
        return dut_qs

    # 进入dut页面，返回dut的类型，例如XQ/XY/SO
    @route.get('/dut/dut_type', url_name='testDemand-type')
    @transaction.atomic
    def get_dut_type(self, project_id: int, key: str):
        check_project_access_by_id(project_id, self.context.request.user)
        project_qs = get_object_or_404(Project, id=project_id)
        dut = project_qs.pdField.filter(key=key).first()
        if not dut:
            return ChenResponse(code=400, status=400, message='被测件不存在，请检查...')
        return ChenResponse(code=200, status=200, data={'dut_type': dut.type})

@api_controller("/dut_upload", tags=['上传源代码/上传需求规格说明解析'],
                auth=JWTAuth(), permissions=[IsAuthenticated])
class UploadController(ControllerBase):
    # 上传zip、7z、rar压缩文件然后计算圈复杂度等信息
    @route.post("/upload_file", url_name='dut-upload-file')
    def upload_code_lines(self, dut_id: int, file: File[UploadedFile]):
        # 获取dut对象
        dut_qs: Dut = get_object_or_404(Dut, id=dut_id)
        check_project_access(dut_qs.project, self.context.request.user)
        # 创建临时目录
        with tempfile.TemporaryDirectory() as tmp_dir:
            # 保存上传的ZIP文件
            zip_path = os.path.join(tmp_dir, file.name)
            with open(zip_path, 'wb') as f:
                for chunk in file.chunks():
                    f.write(chunk)
            # 解压并获取文件路径
            source_root = extract_and_get_paths(zip_path, tmp_dir)
            results = analyze_code_directory(source_root)
            # 判断是否录入了metrics，并且去掉ORM不需要字段
            key_to_remove = {'comment_rate', 'total_lines', 'effective_lines', 'comment_lines', 'code_ratio'}
            create_results = {k: v for k, v in results.items() if k not in key_to_remove}
            # 存在则更新、不存在则创建（一次往返，替代原来的 hasattr + create + update）
            DutMetrics.objects.update_or_create(dut=dut_qs, defaults=create_results)
            # 进行储存
            dut_qs.total_lines = results['total_lines']
            dut_qs.effective_lines = results['effective_lines']
            dut_qs.comment_lines = results['comment_lines']
            dut_qs.save()
            return results

    # 上传需求规格说明.docx进行解析
    @route.post("/upload_xq_docx/", url_name='dut-xq-docx')
    def upload_xq_docx(self, parseChapter: str, file: File[UploadedFile]):
        # 构建临时目录
        with tempfile.TemporaryDirectory() as tmp_dir:
            # 保存到临时目录
            docx_path = os.path.join(tmp_dir, file.name)
            with open(docx_path, 'wb') as f:
                for chunk in file.chunks():
                    f.write(chunk)
            extracter = DocxChapterExtractor(docx_path)
            return extracter.main(parseChapter)
