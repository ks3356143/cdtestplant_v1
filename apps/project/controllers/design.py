from ninja_extra import api_controller, ControllerBase, route
from ninja import Query
from ninja_jwt.authentication import JWTAuth
from ninja_extra.permissions import IsAuthenticated
from ninja.pagination import paginate
from ninja.errors import HttpError
from utils.chen_pagination import MyPagination
from django.db import transaction
from django.shortcuts import get_object_or_404
from typing import List
from utils.chen_response import ChenResponse
from utils.chen_crud import multi_delete_design
from utils.codes import HTTP_INDEX_ERROR
from apps.project.models import Design, Dut, Round, Project
from apps.project.schemas.design import DeleteSchema, DesignFilterSchema, DesignModelOutSchema, DesignTreeReturnSchema, \
    DesignTreeInputSchema, DesignCreateOutSchema, DesignCreateInputSchema, MultiDesignCreateInputSchema
from apps.project.tools.delete_change_key import design_delete_sub_node_key
from utils.smallTools.interfaceTools import conditionNoneToBlank

@api_controller("/project", auth=JWTAuth(), permissions=[IsAuthenticated], tags=['设计需求数据'])
class DesignController(ControllerBase):
    @route.get("/getDesignDemandList", response=List[DesignModelOutSchema], exclude_none=True, url_name="design-list")
    @transaction.atomic
    @paginate(MyPagination)
    def get_design_list(self, datafilter: DesignFilterSchema = Query(...)):
        conditionNoneToBlank(datafilter)
        dut_key = "".join([datafilter.round_id, '-', datafilter.dut_id])
        qs = Design.objects.filter(project__id=datafilter.project_id, dut__key=dut_key,
                                   ident__icontains=datafilter.ident,
                                   name__icontains=datafilter.name,
                                   demandType__contains=datafilter.demandType,
                                   chapter__icontains=datafilter.chapter).order_by('id')
        return qs

    @route.get("/getDesignOne", response=DesignModelOutSchema, url_name='design-one')
    def get_dut(self, project_id: int, key: str):
        design_qs = Design.objects.filter(project_id=project_id, key=key).first()
        if design_qs:
            return design_qs
        raise HttpError(500, "未找到相应的数据")

    # 处理树状数据
    @route.get("/getDesignDemandInfo", response=List[DesignTreeReturnSchema], url_name="design-info")
    def get_design_tree(self, payload: DesignTreeInputSchema = Query(...)):
        qs = Design.objects.filter(project__id=payload.project_id, dut__key=payload.key).order_by('id')
        return qs

    # 添加设计需求
    @route.post("/designDemand/save", response=DesignCreateOutSchema, url_name="design-create")
    @transaction.atomic
    def create_design(self, payload: DesignCreateInputSchema):
        asert_dict = payload.dict(exclude_none=True)
        # 如果识别description为None变为空字符串
        description = asert_dict.get('description')
        # 构造dut_key
        dut_key = "".join([payload.round_key, "-", payload.dut_key])
        # 判重标识-不需要再查询round以后的
        if Design.objects.filter(project__id=payload.project_id, round__key=payload.round_key, dut__key=dut_key,
                                 ident=payload.ident).exists() and asert_dict['ident'] != "":
            return ChenResponse(code=400, status=400, message='研制需求的标识重复，请检查')
        # 查询当前key应该为多少
        design_count = Design.objects.filter(project__id=payload.project_id, dut__key=dut_key).count()
        key_string = ''.join([dut_key, "-", str(design_count)])
        # 查询当前的round_id
        round_instance = Round.objects.get(project__id=payload.project_id, key=payload.round_key)
        dut_instance = Dut.objects.get(project__id=payload.project_id, key=dut_key)
        asert_dict.update({'key': key_string, 'round': round_instance, 'dut': dut_instance, 'title': payload.name})
        asert_dict.pop("round_key")
        asert_dict.pop("dut_key")
        qs = Design.objects.create(**asert_dict)
        return qs

    # 批量增加设计需求，对应前端批量增加页面modal
    @route.post('/designDemand/multi_save', url_name='design-multi-create')
    @transaction.atomic
    def multi_create_design(self, payload: MultiDesignCreateInputSchema):
        project_obj = get_object_or_404(Project, id=payload.project_id)
        dut_obj = project_obj.pdField.filter(key=payload.dut_key).first()
        round_obj = dut_obj.round
        # 当前dut下的design个数
        design_count = Design.objects.filter(project=project_obj, dut=dut_obj).count()
        key_index = design_count
        # 这里根据payload.data批量增加
        bulk_list = []
        for desgin_obj in payload.data:
            design_one = Design(**desgin_obj.model_dump())
            design_one.title = design_one.name
            # 计算出当前key应该为多少
            design_one.key = ''.join([dut_obj.key, "-", str(key_index)])
            key_index += 1
            design_one.level = '2'
            design_one.project = project_obj
            design_one.round = round_obj
            design_one.dut = dut_obj
            bulk_list.append(design_one)
        Design.objects.bulk_create(bulk_list)
        # 为了前端更新，需要返回一个dut_key
        return ChenResponse(status=200, code=200, data={'key': dut_obj.key + '-1'})

    # 更新设计需求
    @route.put("/editDesignDemand/{id}", response=DesignCreateOutSchema, url_name="design-update")
    @transaction.atomic
    def update_design(self, id: int, payload: DesignCreateInputSchema):
        design_search = Design.objects.filter(project__id=payload.project_id, ident=payload.ident,
                                              round__key=payload.round_key)
        # 判断是否和同项目同轮次的标识重复
        if len(design_search) > 1 and payload.ident != '':
            return ChenResponse(code=400, status=400, message='研制需求的标识重复，请检查')
        # 查到当前
        design_qs = Design.objects.get(id=id)
        for attr, value in payload.dict().items():
            if attr == 'project_id' or attr == 'round_key' or attr == 'dut_key':
                continue
            if attr == 'name':
                setattr(design_qs, "title", value)
            setattr(design_qs, attr, value)
        design_qs.save()
        return design_qs

    # 删除设计需求
    @route.delete("/designDemand/delete", url_name="design-delete")
    @transaction.atomic
    def delete_design(self, data: DeleteSchema):
        # 根据其中一个id查询出dut_id
        try:
            design_single = Design.objects.filter(id=data.ids[0])[0]
        except IndexError:
            return ChenResponse(status=500, code=HTTP_INDEX_ERROR, message='您未选择需要删除的内容')
        dut_id = design_single.dut.id
        dut_key = design_single.dut.key
        multi_delete_design(data.ids, Design)
        index = 0
        design_all_qs = Design.objects.filter(dut__id=dut_id).order_by('id')
        for single_qs in design_all_qs:
            design_key = "".join([dut_key, '-', str(index)])
            single_qs.key = design_key
            index = index + 1
            single_qs.save()
            design_delete_sub_node_key(single_qs)
        return ChenResponse(message="设计需求删除成功！")

    # 给复制功能级联选择器查询所有的设计需求
    @route.get("/designDemand/getRelatedDesign", url_name='dut-relatedDesign')
    def getRelatedDesign(self, id: int):
        project_qs = get_object_or_404(Project, id=id)
        # 依次找出round -> dut -> design
        round_qs = project_qs.pField.all()
        data_list = []
        for round in round_qs:
            round_dict = {'label': round.name, 'value': round.id, 'children': []}
            for dut in round.rdField.all():
                dut_dict = {'label': dut.name, 'value': dut.id, 'children': []}
                for design in dut.rsField.all():
                    design_dict = {'label': design.name, 'value': design.id, 'key': design.key}
                    dut_dict['children'].append(design_dict)
                round_dict['children'].append(dut_dict)
            data_list.append(round_dict)
        return ChenResponse(message='获取成功', data=data_list)
