from ninja_extra.controllers import api_controller, ControllerBase, route
from ninja_jwt.authentication import JWTAuth
from ninja_extra.permissions import IsAuthenticated
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.db.models import QuerySet
from docxtpl import DocxTemplate
from apps.createSeiTaiDocument.docXmlUtils import generate_temp_doc
from utils.chen_response import ChenResponse
from apps.project.models import Project, Dut
from apps.createDocument.extensions.documentTime import DocTime
from utils.util import get_str_dict

# @api_controller("/create", tags=['生成产品文档接口'], auth=JWTAuth(), permissions=[IsAuthenticated])
@api_controller("/create", tags=['生成产品文档接口'])
class GenerateSeitaiController(ControllerBase):
    @route.get("/dgDocument", url_name="create-dgDocument")
    @transaction.atomic
    def create_dgDocument(self, id: int):
        # 获取项目Model
        project_obj = get_object_or_404(Project, id=id)
        # 生成大纲需要的基础变量context
        context = {'is_JD': False}
        if project_obj.report_type == '9':
            context['is_JD'] = True
        context['ident'] = project_obj.ident
        # 密级查询字典，根据数据库key值查询
        secret = get_str_dict(project_obj.secret, 'secret')
        context['sec_title'] = secret
        context['sec'] = secret
        context['name'] = project_obj.name
        context['duty_person'] = project_obj.duty_person
        if len(project_obj.member) > 0:
            context['member'] = project_obj.member[0]
        else:
            context['member'] = context['duty_person']
        context['entrust_unit'] = project_obj.entrust_unit

        # 这里插入时间变量
        timer = DocTime(id)
        context.update(**timer.dg_final_time())

        result = generate_temp_doc('dg', id)
        if isinstance(result, dict):
            return ChenResponse(status=400, code=400, message=result.get('msg', 'dg未报出错误原因，反正在生成文档出错'))
        dg_replace_path, dg_seitai_final_path = result
        doc = DocxTemplate(dg_replace_path)

        # 渲染文档
        doc.render(context)

        try:
            doc.save(dg_seitai_final_path)
            return ChenResponse(status=200, code=200, message="最终大纲生成成功！")
        except PermissionError as e:
            return ChenResponse(status=400, code=400, message="模版文件已打开，请关闭后再试，{0}".format(e))

    @route.get('/smDocument', url_name='create-smDocument')
    @transaction.atomic
    def create_smDocument(self, id: int):
        """生成最后说明文档"""
        # 获取项目对象
        project_obj = get_object_or_404(Project, id=id)
        # 首先第二层模版所需变量
        member = project_obj.member[0] if len(project_obj.member) > 0 else project_obj.duty_person
        context = {'name': project_obj.name, 'is_JD': False, 'ident': project_obj.ident,
                   'sec_title': get_str_dict(project_obj.secret, 'secret'),
                   'duty_person': project_obj.duty_person, 'member': member}
        if project_obj.report_type == '9':
            context['is_JD'] = True
        # 提取第一轮测试中源代码 - 用户标识
        round_1 = project_obj.pField.filter(key='0').first()
        duty_so = round_1.rdField.filter(type='SO').first()
        if not duty_so:
            return ChenResponse(code=400, status=400, message="未找到第一轮测试中源代码被测件请添加")
        context['user_ident'] = duty_so.ref

        result = generate_temp_doc('sm', id)
        if isinstance(result, dict):
            return ChenResponse(code=400, status=400, message=result.get('msg', '无错误原因'))
        sm_to_tpl_file, sm_seitai_final_file = result

        # 注册时间变量
        timer = DocTime(id)
        context.update(**timer.sm_final_time())

        doc = DocxTemplate(sm_to_tpl_file)
        doc.render(context)  # 耗时最长，TODO:异步任务处理？或前端等待？
        try:
            doc.save(sm_seitai_final_file)
            return ChenResponse(status=200, code=200, message="最终测试说明生成成功！")
        except PermissionError as e:
            return ChenResponse(status=400, code=400, message="模版文件已打开，请关闭后再试，{0}".format(e))

    @route.get('/jlDocument', url_name='create-jlDocument')
    @transaction.atomic
    def create_jlDocument(self, id: int):
        project_obj = get_object_or_404(Project, id=id)
        # seitai文档所需变量
        ## 1.判断是否为JD
        member = project_obj.member[0] if len(project_obj.member) > 0 else project_obj.duty_person
        context = {'name': project_obj.name, 'ident': project_obj.ident, 'is_JD': False,
                   'sec_title': get_str_dict(project_obj.secret, 'secret'),
                   'duty_person': project_obj.duty_person, 'member': member}
        if project_obj.report_type == '9':
            context['is_JD'] = True
        ## 2.判断被测件是否有需求文档/设计文档/手册文档
        for dut in project_obj.pdField.all():
            if dut.type == 'XQ':
                context['demandDocName'] = dut.name
            if dut.type == 'SJ':
                context['designDocName'] = dut.name
            # TODO:设置手册文档名称-暂时dut没有手册这个类型
            context['manualDocName'] = False
            context['isC'] = True if '1' in project_obj.language else False
            context['isCplus'] = True if '2' in project_obj.language else False

        result = generate_temp_doc('jl', id)
        if isinstance(result, dict):
            return ChenResponse(code=400, status=400, message=result.get('msg', '无错误原因'))
        jl_to_tpl_file, jl_seitai_final_file = result

        # 注入文档变量
        timer = DocTime(id)
        context.update(**timer.jl_final_time())

        doc = DocxTemplate(jl_to_tpl_file)
        doc.render(context)  # 耗时最长，TODO:异步任务处理？或前端等待？
        try:
            doc.save(jl_seitai_final_file)
            return ChenResponse(status=200, code=200, message="最终记录生成成功！")
        except PermissionError as e:
            return ChenResponse(status=400, code=400, message="模版文件已打开，请关闭后再试，{0}".format(e))

    @route.get('/bgDocument', url_name='create-bgDocument')
    @transaction.atomic
    def create_bgDocument(self, id: int):
        """生成最后的报告文档"""
        project_obj = get_object_or_404(Project, id=id)
        # seitai文档所需变量
        ## 1.判断是否为JD
        member = project_obj.member[0] if len(project_obj.member) > 0 else project_obj.duty_person
        context = {'name': project_obj.name, 'ident': project_obj.ident, 'is_JD': False,
                   'sec_title': get_str_dict(project_obj.secret, 'secret'),
                   'duty_person': project_obj.duty_person, 'member': member}
        if project_obj.report_type == '9':
            context['is_JD'] = True
        context['entrust_unit'] = project_obj.entrust_unit

        result = generate_temp_doc('bg', id)
        if isinstance(result, dict):
            return ChenResponse(status=400, code=400, message=result.get('msg', 'bg未报出错误原因，反正在生成文档出错'))
        bg_replace_path, bg_seitai_final_path = result

        # 注入时间
        timer = DocTime(id)
        context.update(**timer.bg_final_time())

        doc = DocxTemplate(bg_replace_path)
        doc.render(context)  # 耗时最长，TODO:异步任务处理？或前端等待？
        try:
            doc.save(bg_seitai_final_path)
            return ChenResponse(status=200, code=200, message="最终报告生成成功！")
        except PermissionError as e:
            return ChenResponse(status=400, code=400, message="模版文件已打开，请关闭后再试，{0}".format(e))

    @route.get('/wtdDocument', url_name='create-wtdDocument')
    @transaction.atomic
    def create_wtdDocument(self, id: int):
        """生成最后的问题单"""
        project_obj = get_object_or_404(Project, id=id)
        # seitai文档所需变量
        member = project_obj.member[0] if len(project_obj.member) > 0 else project_obj.duty_person
        context = {'name': project_obj.name, 'ident': project_obj.ident,
                   'sec_title': get_str_dict(project_obj.secret, 'secret'),
                   'duty_person': project_obj.duty_person, 'member': member}

        result = generate_temp_doc('wtd', id)
        if isinstance(result, dict):
            return ChenResponse(status=400, code=400, message=result.get('msg', 'wtd未报出错误原因，反正在生成文档出错'))
        wtd_replace_path, wtd_seitai_final_path = result
        # 注入时间
        timer = DocTime(id)
        context.update(**timer.wtd_final_time())
        doc = DocxTemplate(wtd_replace_path)
        doc.render(context)  # 耗时最长，TODO:异步任务处理？或前端等待？
        try:
            doc.save(wtd_seitai_final_path)
            return ChenResponse(status=200, code=200, message="问题单生成成功！")
        except PermissionError as e:
            return ChenResponse(status=400, code=400, message="模版文件已打开，请关闭后再试，{0}".format(e))

    @route.get('/hsmDocument', url_name='create-hsmDocument')
    @transaction.atomic
    def create_hsmDocument(self, id: int):
        """生成最后的回归测试说明-（多个文档）"""
        project_obj: Project = get_object_or_404(Project, id=id)
        chinese_round_name: list = ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十']
        # 取非第一轮次
        hround_list: QuerySet = project_obj.pField.exclude(key='0')
        if len(hround_list) < 1:
            return ChenResponse(code=400, status=400, message='无其他轮次，请生成后再试')
        for hround in hround_list:
            # 取出当前轮次key减1就是上一轮次
            cname = chinese_round_name[int(hround.key)]  # 输出二、三...
            member = project_obj.member[0] if len(project_obj.member) > 0 else project_obj.duty_person
            context = {'name': project_obj.name, 'ident': project_obj.ident, 'is_JD': False,
                       'sec_title': get_str_dict(project_obj.secret, 'secret'),
                       'duty_person': project_obj.duty_person, 'member': member, 'round_han': cname,
                       'round_num': int(hround.key) + 1}
            if project_obj.report_type == '9':
                context['is_JD'] = True
            # 受测软件标识从源代码dut取出
            so_dut: Dut = hround.rdField.filter(type='SO').first()
            if not so_dut:
                return ChenResponse(status=400, code=400, message=f'您缺少第{cname}轮的源代码被测件')
            context['user_ref'] = so_dut.ref
            result = generate_temp_doc('hsm', id, round_num=cname)
            if isinstance(result, dict):
                return ChenResponse(status=400, code=400,
                                    message=result.get('msg', 'hsm未报出错误原因，反正在生成文档出错'))
            # 注入时间
            timer = DocTime(id)
            context.update(**timer.hsm_final_time(hround.key))

            hsm_replace_path, hsm_seitai_final_path = result
            doc = DocxTemplate(hsm_replace_path)
            doc.render(context)
            try:
                doc.save(hsm_seitai_final_path)
            except PermissionError as e:
                return ChenResponse(status=400, code=400, message="模版文件已打开，请关闭后再试，{0}".format(e))
        return ChenResponse(status=200, code=200, message="回归测试说明文档生成成功")

    @route.get('/hjlDocument', url_name='create-hjlDocument')
    @transaction.atomic
    def create_hjlDocument(self, id: int):
        """生成最后的回归测试记录-（多个文档）"""
        project_obj: Project = get_object_or_404(Project, id=id)
        chinese_round_name: list = ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十']
        # 取非第一轮次
        hround_list: QuerySet = project_obj.pField.exclude(key='0')
        if len(hround_list) < 1:
            return ChenResponse(code=400, status=400, message='无其他轮次，请生成后再试')
        for hround in hround_list:
            # 取出当前轮次key减1就是上一轮次
            cname = chinese_round_name[int(hround.key)]  # 输出二、三...
            member = project_obj.member[0] if len(project_obj.member) > 0 else project_obj.duty_person
            context = {'name': project_obj.name, 'ident': project_obj.ident, 'is_JD': False,
                       'sec_title': get_str_dict(project_obj.secret, 'secret'),
                       'duty_person': project_obj.duty_person, 'member': member, 'round_han': cname,
                       'round_num': int(hround.key) + 1}
            if project_obj.report_type == '9':
                context['is_JD'] = True

            # 注入时间
            timer = DocTime(id)
            context.update(**timer.hsm_final_time(hround.key))

            result = generate_temp_doc('hjl', id, round_num=cname)
            if isinstance(result, dict):
                return ChenResponse(status=400, code=400,
                                    message=result.get('msg', 'hjl未报出错误原因，反正在生成文档出错'))
            hjl_replace_path, hjl_seitai_final_path = result
            doc = DocxTemplate(hjl_replace_path)
            doc.render(context)
            try:
                doc.save(hjl_seitai_final_path)
            except PermissionError as e:
                return ChenResponse(status=400, code=400, message="模版文件已打开，请关闭后再试，{0}".format(e))
        return ChenResponse(status=200, code=200, message="回归测试记录文档生成成功")
