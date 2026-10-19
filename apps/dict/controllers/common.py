from datetime import date
from ninja_extra import api_controller, ControllerBase, route
from ninja_extra.permissions import IsAuthenticated
from ninja_jwt.authentication import JWTAuth
from typing import Literal
from apps.project.models import Project
from django.db import transaction
from django.contrib.auth import get_user_model
import requests
from utils.chen_response import ChenResponse
from django.db.models import Q
from ninja import Schema

Users = get_user_model()

class AIPostSchema(Schema):
    question: str
    project_type: Literal["cpu", "fpga"]

# AI测试接口
@api_controller("/local_doc_qa", tags=['AI测试接口'],
                auth=JWTAuth(), permissions=[IsAuthenticated])
class AITestController(ControllerBase):
    """AI测试接口：自定义延迟"""

    @route.post("/testing_item")
    def ai_return(self, item: AIPostSchema):
        target_url = "http://192.168.0.63:8777/api/local_doc_qa/testing_item"
        payload = {
            "question": item.question,
            "model_name": "qwen3.5",  # 待变化
            "project_type": item.project_type,
            "streaming": False,
            "user_focus_points": "",
        }
        try:
            resp = requests.post(target_url, json=payload, timeout=120, headers={"Content-Type": "application/json"})
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException:
            # 调用失败，返回 502
            return ChenResponse(data={}, message="调用大模型接口失败，请联系管理员", code=502, status=502)

# 这是其他common内容接口
@api_controller("/system", tags=['通用接口'],
                auth=JWTAuth(), permissions=[IsAuthenticated])
class CommonController(ControllerBase):
    """通用接口类：工作台内的信息"""

    @route.get("/getNoticeList")
    def get_notice(self, pageSize, orderBy, orderType):
        return [
            {"title": "测试管理平台V0.0.2测试发布", "created_at": "2023-09-23",
             "content": "测试管理平台V0.0.2发布，正在进行内部测试.."},
            {"title": "测试管理平台更新公共", "created_at": "2024-06-17",
             "content": "<p>1.修改大纲和报告模版<p><p>2.修复多个bug<p>"},
        ]

    @route.get('/workplace/statistics')
    @transaction.atomic
    def get_statistics(self):
        # 查询用户数量，进行的项目，项目总数，已完成项目数
        user_count = Users.objects.count()
        project_qs = Project.objects.all()
        project_count = project_qs.count()
        project_done_count = project_qs.filter(step='3').count()
        project_processing_count = project_qs.filter(Q(step='1') | Q(step='2')).count()
        return ChenResponse(data={'pcount': project_count, 'ucount': user_count,
                                  'pdcount': project_done_count, 'ppcount': project_processing_count})

    @route.get('/statistics/chart')
    @transaction.atomic
    def get_chart(self):
        """该接口返回当前年份下，每月的项目统计，返回横坐标12个月的字符串以及12个月数据"""
        current_year = date.today().year
        # 用数据库聚合一次算出每月项目数，避免把全年项目全部取到内存里逐条比较
        from django.db.models import Count
        from django.db.models.functions import ExtractMonth
        counts = (Project.objects.filter(beginTime__year=current_year)
                  .annotate(month=ExtractMonth('beginTime'))
                  .values('month')
                  .annotate(count=Count('id')))
        month_map = {row['month']: row['count'] for row in counts}
        month_list = [{'month': i, 'count': month_map.get(i, 0)} for i in range(1, 13)]
        return ChenResponse(status=200, code=200, data=month_list)
