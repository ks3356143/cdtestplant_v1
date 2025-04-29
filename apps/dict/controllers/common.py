from datetime import date
from ninja_extra import api_controller, ControllerBase, route
from apps.project.models import Project
from django.db import transaction
from django.contrib.auth import get_user_model
from utils.chen_response import ChenResponse
from django.db.models import Q

Users = get_user_model()

# 这是其他common内容接口
@api_controller("/system", tags=['通用接口'])
class CommonController(ControllerBase):
    """通用接口类：工作台内的信息"""

    @route.get("/getNoticeList")
    def get_notice(self, pageSize, orderBy, orderType):
        item_list = []
        item1 = {"title": "测试管理平台V0.0.2测试发布", "created_at": "2023-09-23",
                 "content": "测试管理平台V0.0.2发布，正在进行内部测试.."}
        item_list.append(item1)
        item2 = {"title": "测试管理平台更新公共", "created_at": "2024-06-17", "content": "<p>1.修改大纲和报告模版<p><p>2.修复多个bug<p>"}
        item_list.append(item2)
        return item_list

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
        month_list = []
        # 构造数组，里面是字典
        for i in range(12):
            month_dict = {'month': i + 1, 'count': 0}
            month_list.append(month_dict)
        project_qs = Project.objects.all()
        for project in project_qs:
            for m in month_list:
                if m['month'] == project.beginTime.month and project.beginTime.year == current_year:
                    m['count'] += 1
        return ChenResponse(status=200, code=200, data=month_list)
