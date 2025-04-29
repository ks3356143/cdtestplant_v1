from ninja_extra import api_controller, ControllerBase, route
from ninja_jwt.authentication import JWTAuth
from ninja_extra.permissions import IsAuthenticated
from django.db import transaction
from apps.project.models import Round
from apps.project.schemas.round import TreeReturnRound, RoundInfoOutSchema, EditSchemaIn, DeleteSchema, \
    CreateRoundOutSchema, CreateRoundInputSchema
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
