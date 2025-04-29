from ninja_extra import api_controller, ControllerBase, route
from ninja import Query
from apps.project.models import Abbreviation
from ninja_jwt.authentication import JWTAuth
from ninja_extra.permissions import IsAuthenticated
from ninja.pagination import paginate
from utils.chen_pagination import MyPagination
from django.db import transaction
from django.contrib.auth import get_user_model
from typing import List
from utils.chen_crud import multi_delete
from utils.chen_response import ChenResponse
from apps.dict.schema import DeleteSchema, AbbreviationOut, AbbreviationListInputSchema

Users = get_user_model()

@api_controller("/system", tags=['缩略语接口'], auth=JWTAuth(), permissions=[IsAuthenticated])
class AbbreviationController(ControllerBase):
    @route.get("/abbreviation/getlist", response=List[AbbreviationOut], url_name="abbreviation-search")
    @transaction.atomic
    @paginate(MyPagination)
    def get_abbreviation_list(self, payload: AbbreviationListInputSchema = Query(...)):
        for attr, value in payload.__dict__.items():
            if getattr(payload, attr) is None:
                setattr(payload, attr, '')
        qs = Abbreviation.objects.filter(title__icontains=payload.title, des__icontains=payload.des)
        return qs

    # 单独获取
    @route.get("/abbreviation/index", response=List[AbbreviationOut], url_name="abbreviation-all")
    @transaction.atomic
    def get_contact_index(self):
        qs = Abbreviation.objects.all()
        return qs

    @route.post("/abbreviation/save", response=AbbreviationOut, url_name='abbreviation-create')
    @transaction.atomic
    def create_abbreviation(self, data: AbbreviationListInputSchema):
        for attr, value in data.__dict__.items():
            if getattr(data, attr) is None:
                setattr(data, attr, '')
        # 判重key
        assert_dict = data.dict()
        key_qs = Abbreviation.objects.filter(title=data.title)
        if len(key_qs) > 0:
            return ChenResponse(code=400, status=400, message="缩略语重复，请修改...")
        # 正常添加
        qs = Abbreviation.objects.create(**assert_dict)
        return qs

    @route.put("/abbreviation/update/{id}", response=AbbreviationOut, url_name='abbreviation-update')
    @transaction.atomic
    def update_contact(self, id: int, data: AbbreviationListInputSchema):
        for attr, value in data.__dict__.items():
            if getattr(data, attr) is None:
                setattr(data, attr, '')
        key_qs = Abbreviation.objects.filter(title=data.title)
        if len(key_qs) > 1:
            return ChenResponse(code=400, status=400, message="缩略语重复，请修改...")
        # 查询id
        qs = Abbreviation.objects.get(id=id)
        for attr, value in data.__dict__.items():
            setattr(qs, attr, value)
        qs.save()
        return qs

    @route.delete('/abbreviation/delete', url_name='abbreviation-delete')
    @transaction.atomic
    def delete_contact(self, data: DeleteSchema):
        multi_delete(data.ids, Abbreviation)
        return ChenResponse(message='单位或公司删除成功')
