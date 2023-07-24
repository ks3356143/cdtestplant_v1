from ninja_extra import api_controller, ControllerBase, route
from apps.dict.models import Dict, DictItem
from apps.dict.schema import DictItemOut
from typing import List

@api_controller("/system",tags=['字典相关'])
class DictController(ControllerBase):
    @route.get("/dataDict/list",response=List[DictItemOut])
    def get_dict(self,code:str):
        dict_qs = Dict.objects.get(code=code)
        items = dict_qs.dictItem.filter(status=True)
        return items

# 这是其他common内容接口
@api_controller("/system",tags=['通用接口'])
class CommonController(ControllerBase):
    @route.get("/getNoticeList")
    def get_notice(self, pageSize, orderBy, orderType):
        item_list = []
        item1 = {"title": "后台公告1:关于加强后端逻辑能力", "created_at": "2022-09-23",
                 "content": "猫眼可见，undefined 是一个鲁棒只读的属性，表面上相当靠谱"}
        item_list.append(item1)
        item2 = {"title": "后台公告2:关于加强前端样式能力", "created_at": "2023-09-23", "content": "由此可见这个是内容"}
        item_list.append(item2)
        return item_list