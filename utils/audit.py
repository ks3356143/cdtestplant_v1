"""
统一审计日志（GB/T 28452-2012 第三级 7.1.6 安全审计）
在关键安全事件处调用 audit_log() 埋点，事件类型用 EVENT_* 常量分类：
- 用户身份鉴别类：login_success / login_fail / account_lock
- 访问控制/标记类：clearance_change / policy_change / access_denied
- 账号管理类：user_change
- 日志守护类：log_purge（按保留期清理）/ log_purge_denied（越权守护告警）
"""
from django.conf import settings


# 事件类型常量（event_type 前缀，便于筛选）
EVENT_LOGIN_SUCCESS = 'login_success'
EVENT_LOGIN_FAIL = 'login_fail'
EVENT_ACCOUNT_LOCK = 'account_lock'
EVENT_USER_CHANGE = 'user_change'
EVENT_CLEARANCE_CHANGE = 'clearance_change'
EVENT_POLICY_CHANGE = 'policy_change'
EVENT_ACCESS_DENIED = 'access_denied'
EVENT_BUSINESS_CHANGE = 'business_change'
EVENT_LOG_PURGE = 'log_purge'
EVENT_LOG_PURGE_DENIED = 'log_purge_denied'

# 告警类事件（审计页高亮显示）
ALERT_EVENTS = (EVENT_ACCOUNT_LOCK, EVENT_ACCESS_DENIED)


def audit_log(request, event_type: str, detail: str, *, user=None, success: bool = True):
    """
    写入统一审计日志。
    :param request: 当前请求（取 IP/UA），可为 None（非 HTTP 场景如信号）
    :param event_type: EVENT_* 常量之一
    :param detail: 事件描述（中文，供审计员阅读）
    :param user: 事件主体用户对象；None 时尝试 request.user
    :param success: 事件结果（成功/失败）
    """
    import datetime as _dt
    try:
        from apps.system.models import AuditLog
        if user is None and request is not None:
            user = getattr(request, 'user', None)
        actor = None
        username = ''
        role = ''
        if user is not None and getattr(user, 'is_authenticated', False):
            actor = user
            username = getattr(user, 'username', '') or ''
            role = getattr(user, 'role', '') or ''
        from utils.log_util.request_util import get_request_ip, get_browser, get_os
        ip = ''
        ua = ''
        if request is not None:
            try:
                ip = get_request_ip(request)
            except Exception:
                ip = ''
            try:
                ua = str(getattr(request, 'META', {}).get('HTTP_USER_AGENT', ''))
            except Exception:
                ua = ''
        AuditLog.objects.create(
            username=username, role=role, actor=actor,
            event_type=event_type, detail=detail, success=success,
            ip=ip, user_agent=ua[:500],
        )
    except Exception:
        # 审计埋点绝不能影响业务主流程
        pass
