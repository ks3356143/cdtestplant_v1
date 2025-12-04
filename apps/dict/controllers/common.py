from datetime import date
from ninja_extra import api_controller, ControllerBase, route
import json

from apps.project.models import Project
from django.db import transaction
from django.contrib.auth import get_user_model
from utils.chen_response import ChenResponse
from django.db.models import Q
from ninja import Schema

Users = get_user_model()

class AIPostSchema(Schema):
    question: str
    stream: bool

# AI测试接口
@api_controller("/local_doc_qa", tags=['AI测试接口'])
class AITestController(ControllerBase):
    """AI测试接口：自定义延迟"""

    @route.post("/testing_item")
    def ai_return(self, item: AIPostSchema):
        import time
        time.sleep(2)
        res = [
            {
                "demandDescription": "验证外部32MHz品振时钟和内部10KHZ时钟能否正确布线至FPGA内部相应的全局时钟网络，并通过指定缓冲器降低延迟。",
                "title": "时钟布线与缓冲功能测试",
                "children": [
                    {
                        "name": "外部32MHz时钟布线到HCLKBUF级冲测试",
                        "subStep": [
                            {
                                "operation": "配置FPGA逻辑，将外部32MHz晶振输入连接到HCLKBUF缓冲器。",
                                "expect": "时钟信号成功接入HCLKBUF缓冲器，无错误提示。"
                            }, {
                                "operation": "使用示波器或时序分析工具检测HCLKBUF输出端的时钟波形。",
                                "expect": "输出端应稳定输出32MHz时钟信号，频率准确目波形无明显失真。"
                            }, {
                                "operation": "监测从HCLKBUF到各寄存器的时钟路径延迟。",
                                "expect": "各路径延迟保持一致目为最小值，满足分布式延迟最低的变求。"
                            }
                        ]
                    }, {
                        "name": "内部10KHz时钟布线到CLKINT缓冲测试",
                        "subStep": [
                            {
                                "operation": "在FPGA中启用内部10KHz时钟源并将其连接至CLKINT缓冲器。",
                                "expect": "内部时钟信号成功接入CLKINT缓冲器，系统无报错。"
                            }, {
                                "operation": "测量CLKINT输出端的时钟频率。",
                                "expect": "输出端应稳定输出10KHz时钟信号，频率精度符合设计要求。"
                            }, {
                                "operation": "检查CLKINT是否将时钟广播到全局时钟网器",
                                "expect": "时钟能被正常分发至内部各个需要该时钟的模块。"
                            }
                        ]
                    }, {
                        "name": "异常情况下的时钟处理测试",
                        "subStep": [
                            {
                                "operation": "断开外部32MHz晶振输入后尝试进行HCLKBUF配置。",
                                "expect": "系统应报告时钟缺失错误，无法完成正常的时钟分配。"
                            }, {
                                "operation": "人为制造内部10KHz时钟不稳定(如干扰)后再送入CLKINT。",
                                "expect": "CLKINT应拒绝不稳定的时钟或将错误上报给监控机制。"
                            }, {
                                "operation": "同时配置两个时钟但未正确绑定各自缓冲器。",
                                "expect": "系统应阻止非法配置操作，确保每个时钟进入正确的缓冲通道。"
                            }
                        ]
                    }
                ]
            }
        ]
        return {
            "history":[["我是没有用的",json.dumps(res)]]
        }

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
        item2 = {"title": "测试管理平台更新公共", "created_at": "2024-06-17",
                 "content": "<p>1.修改大纲和报告模版<p><p>2.修复多个bug<p>"}
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
