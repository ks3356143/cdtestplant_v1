from ninja_extra import api_controller, ControllerBase, route
from ninja_jwt.authentication import JWTAuth
from ninja_extra.permissions import IsAuthenticated
from django.db import transaction
from apps.project.models import Round, InfluenceArea, InfluenceItem
from apps.project.schemas.round import TreeReturnRound, RoundInfoOutSchema, EditSchemaIn, DeleteSchema, \
    CreateRoundOutSchema, CreateRoundInputSchema, InfluenceItemOutSchema, InfluenceInputSchema
from typing import List
from utils.chen_response import ChenResponse
from apps.project.tools.delete_change_key import round_delete_sub_node_key

@api_controller("/project", auth=JWTAuth(), permissions=[IsAuthenticated], tags=['轮次数据'])
class RoundController(ControllerBase):
    @route.get("/getRoundInfo/{project_id}", response=List[TreeReturnRound], url_name="round-info")
    def get_round_tree(self, project_id):
        qs = Round.objects.filter(project__id=project_id).order_by('key')
        return qs

    @route.get("/getOneRoundInfo", response=RoundInfoOutSchema, url_name="round-one-info")
    def get_round_info(self, projectId: str, round: str):
        qs = Round.objects.filter(project__id=projectId).order_by('id')
        # 这里问题是如果删除中间轮次会出现问题
        qs = qs.get(key=round)
        return qs

    # 更新轮次信息
    @route.put("/round/update/{id}", response=RoundInfoOutSchema, url_name="round-update")
    def update_round(self, id, payload: EditSchemaIn):
        round = self.get_object_or_exception(Round, project__id=payload.project, id=id)
        # 去重功能
        exist_round = Round.objects.filter(project__id=payload.project)
        for exist_r in exist_round:
            if exist_r.id != int(id):
                if exist_r.ident == payload.ident:
                    return ChenResponse(code=400, status=400, message='标识和其他重复')
        for attr, value in payload.dict().items():
            # 不知道为什么多个project
            if attr != "project":
                setattr(round, attr, value)
        round.save()
        return ChenResponse(message="轮次信息更新成功")

    @route.delete("/round/delete", url_name="round-delete")
    @transaction.atomic
    def delete_round(self, project_id: str, data: DeleteSchema):
        # 先查询该project下面的值
        instance = self.get_object_or_exception(Round, project__id=project_id, key=data.key)
        if instance.key == '0':
            return ChenResponse(code=400, status=400, message="无法删除第一轮次数据")
        # （多对多）删除下面case关联的problem关系
        cases = instance.rcField.all()
        for case in cases:
            case.caseField.clear()
        instance.delete()
        # 注意：删除中间key必须发生变化，重写key
        ## 先查询出当前有多少轮次
        round_all_qs = Round.objects.filter(project__id=project_id).order_by('id')
        ## 1.按顺序将轮次的key从1~N排序 2.并且将ident改为key值一样 3.将名称改为对应
        index = 0
        for single_qs in round_all_qs:
            old_key = single_qs.key
            single_qs.key = str(index)
            single_qs.ident = single_qs.ident.replace(f'R{int(old_key) + 1}', f'R{index + 1}')
            single_qs.name = single_qs.name.replace(str(int(old_key) + 1), str(index + 1))
            single_qs.title = single_qs.name
            index = index + 1
            single_qs.save()
            round_delete_sub_node_key(single_qs)
        return ChenResponse(message="删除成功")

    @route.post("/round/save", response=CreateRoundOutSchema, url_name="round-create")
    def create_round(self, project_id: str, data: CreateRoundInputSchema):
        asert_dict = data.dict()
        asert_dict['project_id'] = int(project_id)
        asert_dict['title'] = asert_dict['name']
        # 标识去重
        exist_round = Round.objects.filter(project__id=project_id)
        for exist_r in exist_round:
            if exist_r.id != int(project_id):
                if exist_r.ident == asert_dict['ident']:
                    return ChenResponse(code=400, status=400, message='标识和其他重复')
        Round.objects.create(**asert_dict)
        return ChenResponse(message="新增轮次成功")

    # ~~~影响域分析 - 获取数据和状态~~~
    @route.get("/round/get_influence", response=List[InfluenceItemOutSchema], url_name="round-get-influence-items")
    @transaction.atomic
    def get_influence(self, id: int, round_key: str):
        round_qs = Round.objects.filter(project__id=id, key=round_key)
        round_obj = round_qs.first()
        influence_qs = InfluenceArea.objects.filter(round=round_obj)
        if influence_qs.exists():
            influence = influence_qs.first()
            items_qs = influence.influence_items.all()
            if items_qs.exists():
                return items_qs
        return ChenResponse(status=200, code=25002, data=[])

    # ~~~影响域分析是否有值~~~
    @route.get("/round/get_status_influence", url_name="round-get-status-influence")
    @transaction.atomic
    def get_status_influence(self, id: int, round_key: str):
        round_qs = Round.objects.filter(project__id=id, key=round_key)
        round_obj = round_qs.first()
        influence_qs = InfluenceArea.objects.filter(round=round_obj)
        if influence_qs.exists():
            influence = influence_qs.first()
            items_qs = influence.influence_items.all()
            if items_qs.exists():
                return ChenResponse(status=200, code=25005, data=True)
        return ChenResponse(status=200, code=25006, data=False)

    # ~~~影响域分析 - 修改或新增~~~
    @route.post("/round/create_influence", url_name="round-influence-create")
    @transaction.atomic
    def post_influence(self, data: InfluenceInputSchema):
        round_obj = Round.objects.filter(project_id=data.id, key=data.round_key).first()
        influence_area_qs = InfluenceArea.objects.filter(round=round_obj)
        if influence_area_qs.exists():
            influence_area_obj = influence_area_qs.first()
            influence_area_obj.influence_items.all().delete()
            # 先删除再创建
            data_list = []
            for item in data.item_list:
                new_item = InfluenceItem(influence=influence_area_obj,
                                         change_type=item.change_type,
                                         change_influ=item.change_influ,
                                         change_des=item.change_des,
                                         effect_cases=item.effect_cases)
                data_list.append(new_item)
            InfluenceItem.objects.bulk_create(data_list)
        else:
            parent_obj = InfluenceArea.objects.create(round=round_obj)
            data_list = []
            for item in data.item_list:
                new_item = InfluenceItem(influence=parent_obj,
                                         change_type=item.change_type,
                                         change_influ=item.change_influ,
                                         change_des=item.change_des,
                                         effect_cases=item.effect_cases)
                data_list.append(new_item)
            InfluenceItem.objects.bulk_create(data_list)
