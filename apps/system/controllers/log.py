from typing import List
from datetime import datetime, timedelta
from ninja_extra import api_controller, ControllerBase, route
from ninja_jwt.authentication import JWTAuth
from ninja_extra.permissions import IsAuthenticated
from django.db.transaction import atomic
from apps.system.models import LoginLog, OperationLog
from utils.chen_pagination import MyPagination
from ninja.pagination import paginate
from ninja import Query
from utils.chen_response import ChenResponse
# 导入schemas
from apps.system.schemas.log import LogOutSchema, OperationLogOutSchema, LoginLogOutSchema, DeleteInputSchema

@api_controller("/system/log", auth=JWTAuth(), permissions=[IsAuthenticated], tags=['日志相关'])
class LogController(ControllerBase):
    @route.get('/list', response=List[LogOutSchema])
    @atomic
    def get_login_log(self):
        """获取当前用户的登录日志"""
        user = self.context.request.user
        log_qs = LoginLog.objects.filter(creator=user)
        logs = log_qs[:5]
        return logs

    @route.get('/operations', response=List[OperationLogOutSchema])
    @atomic
    def get_operations(self):
        """获取当前用户操作日志"""
        user = self.context.request.user
        log_qs = OperationLog.objects.filter(creator=user)
        return log_qs[:5]

    # 操作日志：查询
    @route.get('/operationsPagination', response=List[OperationLogOutSchema])
    @atomic
    @paginate(MyPagination)
    def get_operations_pagination(self, request_username: str = None):
        logs = OperationLog.objects.all()
        if request_username is None:
            request_username = ''
        qs = logs.filter(request_username__icontains=request_username)
        return qs

    # 操作日志：根据请求参数天数删除
    @route.get('/operationsDel')
    @atomic
    def operation_delete_log(self, payload: DeleteInputSchema = Query(...)):
        time = datetime.now() - timedelta(days=payload.day)
        log_qs = OperationLog.objects.filter(create_datetime__lt=time)
        log_qs.delete()
        if payload.day > 0:
            return ChenResponse(message=f'删除{payload.day}天前数据成功')
        else:
            return ChenResponse(message='全部日志删除成功')

    # 登录日志：查询
    @route.get('/loginLogsList', response=List[LoginLogOutSchema])
    @atomic
    @paginate(MyPagination)
    def get_login_logs(self, username: str = None):
        logs = LoginLog.objects.all()
        if username is None:
            username = ''
        qs = logs.filter(username__icontains=username)
        return qs

    # 登录日志：根据请求参数天数删除
    @route.get('/loginLogsDel')
    @atomic
    def login_logs_delete(self, payload: DeleteInputSchema = Query(...)):
        time = datetime.now() - timedelta(days=payload.day)
        log_qs = LoginLog.objects.filter(create_datetime__lt=time)
        log_qs.delete()
        if payload.day > 0:
            return ChenResponse(message=f'删除{payload.day}天前数据成功')
        else:
            return ChenResponse(message='全部日志删除成功')
