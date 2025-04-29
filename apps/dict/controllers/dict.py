from ninja_extra import api_controller, ControllerBase, route
from ninja import Query
from apps.dict.models import Dict, DictItem
from ninja_jwt.authentication import JWTAuth
from ninja_extra.permissions import IsAuthenticated, IsAdminUser
from ninja.pagination import paginate
from ninja.errors import HttpError
from utils.chen_pagination import MyPagination
from django.db import transaction
from typing import List
from utils.chen_crud import multi_delete
from utils.chen_response import ChenResponse
from apps.dict.schema import DictOut, DictIndexInput, ChangeStautsSchemaInput, DictItemInput, DictItemOut, \
    DictItemChangeSrotInput, DictItemCreateInputSchema, DictItemUpdateInputSchema, DeleteSchema, \
    DictItemFastCreateInputSchema, DictStdItemCreateInputSchema

@api_controller("/system", tags=['字典相关'], auth=JWTAuth(), permissions=[IsAuthenticated])
class DictController(ControllerBase):
    @route.get("/dataDict/list", response=List[DictItemOut], url_name="dict-list")
    def get_dict(self, code: str):
        """传入code类型：例如testType，返回字典Item信息"""
        dict_qs = Dict.objects.get(code=code)
        items = dict_qs.dictItem.filter(status='1')
        return items

    @route.get("/dataDict/index", response=List[DictOut], url_name="dict-index")
    @transaction.atomic
    @paginate(MyPagination)
    def get_dict_index(self, payload: DictIndexInput = Query(...)):
        for attr, value in payload.__dict__.items():
            if getattr(payload, attr) is None:
                setattr(payload, attr, '')
        # 处理时间
        if payload.update_datetime_start == '':
            payload.update_datetime_start = "2000-01-01"
        if payload.update_datetime_end == '':
            payload.update_datetime_end = '5000-01-01'
        date_list = [payload.update_datetime_start, payload.update_datetime_end]
        qs = Dict.objects.filter(name__icontains=payload.name, remark__icontains=payload.remark,
                                 code__icontains=payload.code, status__icontains=payload.status,
                                 update_datetime__range=date_list)
        return qs

    @route.put("/dataDict/changeStatus", url_name="dict-changeStatus", permissions=[IsAdminUser])
    @transaction.atomic
    def change_dict_status(self, data: ChangeStautsSchemaInput):
        qs = Dict.objects.get(id=data.id)
        qs.status = data.status
        qs.save()
        return ChenResponse(code=200, status=200, message="修改状态成功")

    @route.put("/dataDict/changeItemStatus", url_name="dict-changeItemStatus", permissions=[IsAdminUser])
    @transaction.atomic
    def change_dict_item_status(self, data: ChangeStautsSchemaInput):
        qs = DictItem.objects.get(id=data.id)
        qs.status = data.status
        qs.save()
        return ChenResponse(code=200, status=200, message="修改状态成功")

    # 有dict的id查询其中的dictItem数据
    @route.get("/dataDict/dictItemAll", response=List[DictItemOut], url_name='dictitem-list')
    @transaction.atomic
    @paginate(MyPagination)
    def get_dictItem_list(self, payload: DictItemInput = Query(...)):
        for attr, value in payload.__dict__.items():
            if getattr(payload, attr) is None:
                setattr(payload, attr, '')
        # 处理时间
        if payload.update_datetime_start == '':
            payload.update_datetime_start = "2000-01-01"
        if payload.update_datetime_end == '':
            payload.update_datetime_end = '5000-01-01'
        date_list = [payload.update_datetime_start, payload.update_datetime_end]
        # 先对dict_id进行查询
        dict_qs = Dict.objects.get(id=payload.dict_id)
        # 反向连接
        qs = dict_qs.dictItem.filter(update_datetime__range=date_list, status__icontains=payload.status,
                                     key__icontains=payload.key, title__icontains=payload.title,
                                     show_title__icontains=payload.show_title).order_by('sort')
        return qs

    # 更改dictItem的sort字段接口
    @route.put("/dataDict/numberOperation", url_name="dictitem-changesort")
    @transaction.atomic
    def change_item_sort(self, data: DictItemChangeSrotInput):
        qs = DictItem.objects.get(id=data.id)
        qs.sort = data.numberValue
        qs.save()
        return ChenResponse(code=200, status=200, message='排序序号更新成功')

    # 新增dictItem
    @route.post("/dataDict/saveitem", response=DictItemOut, url_name="dictitem-save")
    @transaction.atomic
    def save_item(self, payload: DictItemCreateInputSchema):
        # 先根据dict_id查询出dict
        dict_qs = Dict.objects.get(id=payload.dict_id)
        qs1 = dict_qs.dictItem.filter(title=payload.title)
        if len(qs1) > 0:
            return ChenResponse(code=400, status=400, message='字典标签重复，请检查')
        # 计算key值应该为多少
        key_number = str(len(dict_qs.dictItem.all()) + 1)
        asert_dict = payload.dict(exclude_none=True)
        asert_dict.pop('dict_id')
        asert_dict.update({'dict': dict_qs, 'key': key_number})
        qs = DictItem.objects.create(**asert_dict)
        return qs

    # 更新dictitem数据
    @route.put("/dataDict/update/{id}", response=DictItemOut, url_name='dictitem-update')
    @transaction.atomic
    def update(self, id: int, payload: DictItemUpdateInputSchema):
        dictitem_qs = DictItem.objects.get(id=id)
        for attr, value in payload.dict().items():
            setattr(dictitem_qs, attr, value)
        dictitem_qs.save()
        return dictitem_qs

    # 删除dictItem数据
    @route.delete("/dictType/realDeleteItem", url_name="dictitem-delete", permissions=[IsAdminUser])
    @transaction.atomic
    def delete_dictitem(self, data: DeleteSchema):
        # 根据其中一个id查询出dict的id
        dictItem_single = DictItem.objects.filter(id=data.ids[0])[0]
        dict_id = dictItem_single.dict.id
        multi_delete(data.ids, DictItem)
        index = 1
        qs = Dict.objects.get(id=dict_id).dictItem.all()
        for qs_item in qs:
            qs_item.key = str(index)
            index = index + 1
            qs_item.save()
        return ChenResponse(message="字典条目删除成功！")

    # 快速新增dictItem数据
    @route.post("/dataDict/fastSave", url_name="dictitem-save-fast", permissions=[IsAuthenticated])
    @transaction.atomic
    def save_fast_dictitem(self, data: DictItemFastCreateInputSchema):
        # 首先根据data.code查询出是哪个Dict
        dict_single = Dict.objects.filter(code=data.code).first()
        # 判断是否有该dict
        if dict_single:
            # 再判断是否dictItem重复
            qs = dict_single.dictItem.filter(title=data.title)
            if len(qs) > 0:
                return ChenResponse(code=400, status=400, message='字典标签重复，请检查')
            # 查看key值应该为多少了
            key_number = str(len(dict_single.dictItem.all()) + 1)
            DictItem.objects.create(title=data.title,
                                    key=key_number,
                                    show_title=data.title,
                                    dict=dict_single)
        else:
            raise HttpError(404, "未查询到字典，请创建字典数据后进行")
        return ChenResponse(message="新增成功")

    # 快速新增依据标准dictItem数据 - 输入更变为code
    @route.post("/dataDict/saveStdItem", response=DictItemOut, url_name="dictitem-save")
    @transaction.atomic
    def save(self, payload: DictStdItemCreateInputSchema):
        # 先根据dict_id查询出dict
        dict_qs = Dict.objects.get(code=payload.code)
        qs1 = dict_qs.dictItem.filter(title=payload.title)
        if len(qs1) > 0:
            return ChenResponse(code=400, status=400, message='字典标签重复，请检查')
        # 计算key值应该为多少
        key_number = str(len(dict_qs.dictItem.all()) + 1)
        asert_dict = payload.dict(exclude_none=True)
        asert_dict.pop('code')
        asert_dict.update({'dict': dict_qs, 'key': key_number})
        qs=DictItem.objects.create(**asert_dict)
        return qs
