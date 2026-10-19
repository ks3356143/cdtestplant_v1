from utils.chen_ninja import ChenNinjaAPI
from ninja.errors import HttpError
from ninja_extra.exceptions import PermissionDenied
# 导入orjson解析器，渲染器，提升性能
from cdtestplant_v1.parser import MyParser
from cdtestplant_v1.renderer import MyRenderer
# swagger-ui配置
from ninja import Swagger
# 错误码
from utils.codes import PROJECT_ENDTIME_ERROR_CODE

api = ChenNinjaAPI(
    title="测试管理平台API",
    description="测试管理平台的接口一系列接口函数",
    urls_namespace="cdtestplant_v1",
    parser=MyParser(),
    renderer=MyRenderer(),
    docs=Swagger({"persistAuthorization": True})
)

# 捕获HttpError - 注意这种方式不过create_response函数，需自己定义
@api.exception_handler(HttpError)
def in_program_exception_handler(request, exc):
    # 合法的 HTTP 状态码原样返回（400/401/404/405…），自定义业务码统一落到 500
    raw = getattr(exc, 'status_code', 500)
    status = raw if isinstance(raw, int) and 400 <= raw <= 599 else 500
    data = {}
    if raw == PROJECT_ENDTIME_ERROR_CODE:
        data['flag'] = PROJECT_ENDTIME_ERROR_CODE
    return api.create_response(request, status=status, message=exc.message, data=data)

# 越权拒绝统一审计告警（7.1.6）：所有 403（DAC/标记/管理权限）记为安全告警事件
# 同一 主体+IP+路径 30 秒窗口去重——探测脚本批量触发时审计表不被刷爆（但每次仍拒绝）
@api.exception_handler(PermissionDenied)
def access_denied_exception_handler(request, exc: PermissionDenied):
    from utils.audit import audit_log, EVENT_ACCESS_DENIED
    detail = getattr(exc, 'detail', None) or getattr(exc, 'message', '越权访问被拒绝')
    if not isinstance(detail, str):
        detail = str(detail)
    user = getattr(request, 'user', None)
    username = getattr(user, 'username', '') if user is not None and getattr(user, 'is_authenticated', False) else ''
    from django.core.cache import cache
    dedup_key = f"audit_deny:{username}:{request.META.get('REMOTE_ADDR', '')}:{request.path}"
    if cache.get(dedup_key) is None:
        cache.set(dedup_key, 1, 30)
        audit_log(request, EVENT_ACCESS_DENIED,
                  f'安全告警：越权访问被拒绝 {request.method} {request.path} —— {detail}',
                  success=False)
    return api.create_response(request, status=403, message=detail, data={'code': 403})

# 自动寻找每个app下面controllers.py中被@api_controller修饰的类
api.auto_discover_controllers()
