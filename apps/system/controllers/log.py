from typing import List
from datetime import datetime, timedelta
from ninja_extra import api_controller, ControllerBase, route
from ninja_jwt.authentication import JWTAuth
from ninja_extra.permissions import IsAuthenticated
from utils.permissions import IsAuditor
from django.db.transaction import atomic
from django.db.models import Q
from apps.system.models import AuditLog, LoginLog, OperationLog
from utils.chen_pagination import MyPagination
from ninja.pagination import paginate
from ninja import Query
from utils.chen_response import ChenResponse
from utils.audit import audit_log, EVENT_LOG_PURGE, EVENT_LOG_PURGE_DENIED
# 导入schemas
from apps.system.schemas.log import (LogOutSchema, OperationLogOutSchema, LoginLogOutSchema, DeleteInputSchema,
                                     AuditLogOutSchema, AuditFilterSchema)

# 审计日志最小保留期（天）：日志保护（7.1.6 判定标准3）——审计员也只能清理超过保留期的旧日志，
# 全清一律拒绝；清理动作自身审计留痕，非审计员触发则告警
AUDIT_MIN_RETENTION_DAYS = 30

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

    # 操作日志：查询（审计员专属）
    @route.get('/operationsPagination', response=List[OperationLogOutSchema], permissions=[IsAuthenticated, IsAuditor])
    @atomic
    @paginate(MyPagination)
    def get_operations_pagination(self, request_username: str = None):
        logs = OperationLog.objects.all()
        if request_username is None:
            request_username = ''
        qs = logs.filter(request_username__icontains=request_username)
        return qs

    # 操作日志：根据请求参数天数删除（审计员专属，受最小保留期保护）
    @route.get('/operationsDel', permissions=[IsAuthenticated, IsAuditor])
    @atomic
    def operation_delete_log(self, payload: DeleteInputSchema = Query(...)):
        return self._protected_log_purge(payload.day, OperationLog, '操作日志')

    # 登录日志：查询（审计员专属）
    @route.get('/loginLogsList', response=List[LoginLogOutSchema], permissions=[IsAuthenticated, IsAuditor])
    @atomic
    @paginate(MyPagination)
    def get_login_logs(self, username: str = None):
        logs = LoginLog.objects.all()
        if username is None:
            username = ''
        qs = logs.filter(username__icontains=username)
        return qs

    # 登录日志：根据请求参数天数删除（审计员专属，受最小保留期保护）
    @route.get('/loginLogsDel', permissions=[IsAuthenticated, IsAuditor])
    @atomic
    def login_logs_delete(self, payload: DeleteInputSchema = Query(...)):
        return self._protected_log_purge(payload.day, LoginLog, '登录日志')

    # ~~~~~~~~~~~~ 统一审计日志（7.1.6）：多维度检索 + 告警事件 + 防篡改 ~~~~~~~~~~~~

    # 统一审计日志：多条件检索（账号/时间/事件类型/告警/IP）
    @route.get('/auditLogList', response=List[AuditLogOutSchema], permissions=[IsAuthenticated, IsAuditor])
    @atomic
    @paginate(MyPagination)
    def get_audit_logs(self, filters: AuditFilterSchema = Query(...)):
        condition = Q()
        if filters.username:
            condition &= Q(username__icontains=filters.username)
        if filters.event_type:
            condition &= Q(event_type=filters.event_type)
        if filters.only_alerts:
            condition &= Q(event_type__in=['account_lock', 'access_denied', 'log_purge_denied'])
        if filters.start_time:
            condition &= Q(create_datetime__gte=filters.start_time)
        if filters.end_time:
            condition &= Q(create_datetime__lte=filters.end_time + timedelta(days=1))
        if filters.ip:
            condition &= Q(ip__icontains=filters.ip)
        return AuditLog.objects.filter(condition)

    # 事件类型可用值（前端筛选下拉）
    @route.get('/auditEventTypes', permissions=[IsAuthenticated, IsAuditor])
    @atomic
    def get_audit_event_types(self):
        return ChenResponse(data=list(AuditLog.objects.values_list('event_type', flat=True).distinct()))

    def _protected_log_purge(self, day: int, model, label: str):
        """审计日志按保留期保护删除：全清/短于最小保留期一律拒绝并告警；合法清理自身留痕"""
        request = self.context.request
        if day < AUDIT_MIN_RETENTION_DAYS:
            audit_log(request, EVENT_LOG_PURGE_DENIED,
                      f'安全告警：越权日志删除尝试被拒绝（{label}，day={day}，须≥{AUDIT_MIN_RETENTION_DAYS}天），'
                      f'审计踪迹受保护不被篡改', success=False)
            return ChenResponse(status=403, code=403,
                                message=f'审计日志受保护：仅能清理 {AUDIT_MIN_RETENTION_DAYS} 天前的日志，禁止全清')
        time = datetime.now() - timedelta(days=day)
        count = model.objects.filter(create_datetime__lt=time).count()
        model.objects.filter(create_datetime__lt=time).delete()
        audit_log(request, EVENT_LOG_PURGE, f'{label}按保留期清理：删除 {day} 天前数据 {count} 条（保留期内日志不可删）')
        return ChenResponse(message=f'清理成功：删除{day}天前{label}数据 {count} 条')
