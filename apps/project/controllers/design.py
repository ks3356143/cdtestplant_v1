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
from apps.project.models import Design, Dut, Round
from apps.project.schemas.design import DeleteSchema, DesignFilterSchema, DesignModelOutSchema, DesignTreeReturnSchema, \
    DesignTreeInputSchema, DesignCreateOutSchema, DesignCreateInputSchema

@api_controller("/project", auth=JWTAuth(), permissions=[IsAuthenticated], tags=['设计需求数据'])
class DesignController(ControllerBase):
    @route.get("/getDesignDemandList", response=List[DesignModelOutSchema], exclude_none=True, url_name="design-list")
    @transaction.atomic
    @paginate(MyPagination)
    def get_design_list(self, datafilter: DesignFilterSchema = Query(...)):
        for attr, value in datafilter.__dict__.items():
            if getattr(datafilter, attr) is None:
                setattr(datafilter, attr, '')
        dut_key = "".join([datafilter.round_id, '-', datafilter.dut_id])
        qs = Design.objects.filter(project__id=datafilter.project_id, dut__key=dut_key,
                                   ident__icontains=datafilter.ident,
                                   name__icontains=datafilter.name,
                                   demandType__contains=datafilter.demandType).order_by("key")
        return qs

    # 处理树状数据
    @route.get("/getDesignDemandInfo", response=List[DesignTreeReturnSchema], url_name="design-info")
    def get_design_tree(self, payload: DesignTreeInputSchema = Query(...)):
        qs = Design.objects.filter(project__id=payload.project_id, dut__key=payload.key)
        return qs

    # 添加测试需求
    @route.post("/designDemand/save", response=DesignCreateOutSchema, url_name="design-create")
    @transaction.atomic
    def create_design(self, payload: DesignCreateInputSchema):
        asert_dict = payload.dict(exclude_none=True)
        # 构造dut_key
        dut_key = "".join([payload.round_key, "-", payload.dut_key])
        # 判重标识-不需要再查询round以后的
        if Design.objects.filter(project__id=payload.project_id, round__key=payload.round_key, dut__key=dut_key,
                                 ident=payload.ident).exists():
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

    # 更新测试需求
    @route.put("/editDesignDemand/{id}", url_name="design-update")
    @transaction.atomic
    def update_design(self, id: int, payload: DesignCreateInputSchema):
        design_search = Design.objects.filter(project__id=payload.project_id, ident=payload.ident)
        # 判断是否和同项目同轮次的标识重复
        if len(design_search) > 1:
            return ChenResponse(code=400, status=400, message='研制需求的标识重复，请检查')
        # 查到当前
        design_qs = Design.objects.get(id=id)
        for attr, value in payload.dict().items():
            print(attr)
            if attr == 'project_id' or attr == 'round_key' or attr == 'dut_key':
                continue
            if attr == 'name':
                setattr(design_qs, "title", value)
            setattr(design_qs, attr, value)
        design_qs.save()
        return ChenResponse(message="研制需求更新成功!")

    # 删除被测件
    @route.delete("/designDemand/delete", url_name="design-delete")
    @transaction.atomic
    def delete_design(self, data: DeleteSchema):
        # 根据其中一个id查询出dut_id
        design_single = Design.objects.filter(id=data.ids[0])[0]
        dut_id = design_single.dut.id
        dut_key = design_single.dut.key
        multi_delete(data.ids, Design)
        index = 0
        design_all_qs = Design.objects.filter(dut__id=dut_id)
        for single_qs in design_all_qs:
            design_key = "".join([dut_key,'-',str(index)])
            single_qs.key = design_key
            index = index + 1
            single_qs.save()
        return ChenResponse(message="研制需求删除成功！")
