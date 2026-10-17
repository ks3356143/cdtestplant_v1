"""
统一审计日志（GB/T 28452-2012 第三级 7.1.6 安全审计）
在关键安全事件处调用 audit_log() 埋点，事件类型用 EVENT_* 常量分类：
- 用户身份鉴别类：login_success / login_fail / account_lock
- 访问控制/标记类：clearance_change / policy_change / access_denied
- 账号管理类：user_change
- 日志守护类：log_purge（按保留期清理）/ log_purge_denied（越权守护告警）
"""

# 事件类型常量（唯一真相源；前端审计页的标签/告警高亮以此对应）
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
EVENT_INTEGRITY_CHECK = 'integrity_check'
EVENT_INTEGRITY_BROKEN = 'integrity_broken'

# 告警类事件（审计页红色高亮 + "只看告警"筛选）
ALERT_EVENTS = (EVENT_ACCOUNT_LOCK, EVENT_ACCESS_DENIED, EVENT_LOG_PURGE_DENIED, EVENT_INTEGRITY_BROKEN)

# 事件类型中文标签（唯一真相源；审计页下拉/标签消费 /auditEventTypes 接口）
EVENT_LABELS = {
    EVENT_LOGIN_SUCCESS: '登录成功',
    EVENT_LOGIN_FAIL: '鉴别失败',
    EVENT_ACCOUNT_LOCK: '账号锁定告警',
    EVENT_USER_CHANGE: '账号管理',
    EVENT_CLEARANCE_CHANGE: '标记变更',
    EVENT_POLICY_CHANGE: '策略变更',
    EVENT_ACCESS_DENIED: '越权访问告警',
    EVENT_BUSINESS_CHANGE: '业务数据变更',
    EVENT_LOG_PURGE: '审计日志清理',
    EVENT_LOG_PURGE_DENIED: '日志删除告警',
    EVENT_INTEGRITY_CHECK: '完整性核查',
    EVENT_INTEGRITY_BROKEN: '数据篡改告警',
}


def get_event_types():
    """事件类型清单（供审计页下拉与统计标签）：[{code, label, alert}]"""
    return [{'code': code, 'label': EVENT_LABELS.get(code, code), 'alert': code in ALERT_EVENTS}
            for code in EVENT_LABELS]


def audit_log(request, event_type: str, detail: str, *, user=None, username: str = None, success: bool = True):
    """
    写入统一审计日志。
    :param request: 当前请求（取 IP/UA），可为 None（非 HTTP 场景）
    :param event_type: EVENT_* 常量之一
    :param detail: 事件描述（中文，供审计员阅读）
    :param user: 事件主体用户对象；None 时尝试 request.user
    :param username: 主体账号；未认证场景（登录失败/锁定）取不到 request.user 时显式指定
    :param success: 事件结果（成功/失败）
    """
    try:
        from apps.system.models import AuditLog
        if user is None and request is not None:
            user = getattr(request, 'user', None)
        actor = None
        uname = ''
        role = ''
        if user is not None and getattr(user, 'is_authenticated', False):
            actor = user
            uname = getattr(user, 'username', '') or ''
            role = getattr(user, 'role', '') or ''
        elif username:
            uname = username
        ip = ''
        ua = ''
        if request is not None:
            from utils.log_util.request_util import get_request_ip
            ip = get_request_ip(request)
            ua = str(getattr(request, 'META', {}).get('HTTP_USER_AGENT', '') or '')
        AuditLog.objects.create(
            username=uname, role=role, actor=actor,
            event_type=event_type, detail=detail, success=success,
            ip=ip, user_agent=ua[:500],
        )
    except Exception:
        # 审计埋点绝不能影响业务主流程
        pass
