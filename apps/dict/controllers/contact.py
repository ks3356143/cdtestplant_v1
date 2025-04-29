from ninja_extra import api_controller, ControllerBase, route
from ninja import Query
from apps.project.models import Contact
from ninja_jwt.authentication import JWTAuth
from ninja_extra.permissions import IsAuthenticated
from ninja.pagination import paginate
from utils.chen_pagination import MyPagination
from django.db import transaction
from typing import List
from utils.chen_crud import multi_delete
from utils.chen_response import ChenResponse
from apps.dict.schema import DeleteSchema, ContactListInputSchema, ContactOut

# 公司信息处理接口
@api_controller("/system", tags=['公司信息相关'], auth=JWTAuth(), permissions=[IsAuthenticated])
class ContactController(ControllerBase):
    @route.get("/contact/getlist", response=List[ContactOut], url_name="contact-search")
    @transaction.atomic
    @paginate(MyPagination)
    def get_contact_list(self, payload: ContactListInputSchema = Query(...)):
        for attr, value in payload.__dict__.items():
            if getattr(payload, attr) is None:
                setattr(payload, attr, '')
        if payload.key == '':
            qs = Contact.objects.filter(name__icontains=payload.name, entrust_person__icontains=payload.entrust_person,
                                        addr__icontains=payload.addr)
        else:
            qs = Contact.objects.filter(name__icontains=payload.name, entrust_person__icontains=payload.entrust_person,
                                        key=int(payload.key), addr__icontains=payload.addr)
        return qs

    # 单独获取
    @route.get("/contact/index", response=List[ContactOut], url_name="contact-all")
    @transaction.atomic
    def get_contact_index(self):
        qs = Contact.objects.all()
        return qs

    @route.post("/contact/save", response=ContactOut, url_name='contact-create')
    @transaction.atomic
    def create_contact(self, data: ContactListInputSchema):
        for attr, value in data.__dict__.items():
            if getattr(data, attr) is None:
                setattr(data, attr, '')
        # 判重key -> key可能为空
        if data.key == '':
            data.key = 0
        assert_dict = data.dict()
        key_qs = Contact.objects.filter(key=str(data.key))
        if len(key_qs) > 0:
            return ChenResponse(code=400, status=400, message="公司或单位的编号重复，请修改")
        # 全称判重
        name_qs = Contact.objects.filter(name=data.name)
        if len(name_qs) > 0:
            return ChenResponse(code=400, status=400, message="全称重复，请修改")

        # 去掉key
        assert_dict.pop("key")
        assert_dict['key'] = 999999
        qs = Contact.objects.create(**assert_dict)
        qs.key = qs.id
        qs.save()
        return qs

    @route.put("/contact/update/{id}", response=ContactOut, url_name='contact-update')
    @transaction.atomic
    def update_contact(self, id: int, data: ContactListInputSchema):
        for attr, value in data.__dict__.items():
            if getattr(data, attr) is None:
                setattr(data, attr, '')
        qs = Contact.objects.filter(id=id).first()
        if qs:
            if qs.key != data.key:
                key_qs = Contact.objects.filter(key=str(data.key))
                if len(key_qs) > 0:
                    return ChenResponse(code=400, status=400, message="公司或单位的编号重复，请修改")
            if qs.name != data.name:
                name_qs = Contact.objects.filter(name=data.name)
                if len(name_qs) > 0:
                    return ChenResponse(code=400, status=400, message="全称重复，请修改")
            # 更新联系人数据
            for attr, value in data.__dict__.items():
                setattr(qs, attr, value)
            qs.save()
            return qs

    @route.delete('/contact/delete', url_name='contact-delete')
    @transaction.atomic
    def delete_contact(self, data: DeleteSchema):
        multi_delete(data.ids, Contact)
        return ChenResponse(message='单位或公司删除成功')
