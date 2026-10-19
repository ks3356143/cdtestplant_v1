"""
日志中间件
"""
import json
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.utils.deprecation import MiddlewareMixin
from apps.system.models import OperationLog
from apps.user.models import Users
from utils.log_util.request_util import (
    get_browser,
    get_os,
    get_request_data,
    get_request_ip,
    get_request_path,
)
from utils.sensitive import mask_sensitive

class ApiLoggingMiddleware(MiddlewareMixin):
    """
    用于记录API访问日志中间件
    """

    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.enable = getattr(settings, 'API_LOG_ENABLE', None) or False
        self.methods = getattr(settings, 'API_LOG_METHODS', None) or set()

    @classmethod
    def __handle_request(cls, request):
        request.request_ip = get_request_ip(request)
        request.request_data = get_request_data(request)
        request.request_path = get_request_path(request)

    def __handle_response(self, request, response):
        # request_data,request_ip由PermissionInterfaceMiddleware中间件中添加的属性
        body = getattr(request, 'request_data', {})
        # 敏感信息脱敏后再落库（7.1.8）：口令等全掩、手机/邮箱部分打码，
        # 避免用户的敏感数据长期残留在操作日志这类动态记录介质中。
        body = mask_sensitive(body)
        if not hasattr(response, 'data') or not isinstance(response.data, dict):
            response.data = {}
        try:
            if not response.data and response.content:
                content = json.loads(response.content.decode())
                response.data = content if isinstance(content, dict) else {}
        except Exception:
            return
        if getattr(request, 'user', None) is None:
            return
        user = request.user
        if isinstance(user, AnonymousUser):
            return
        # 如果操作日志在settings.API_OPERATION_EXCLUDE_START记录的路径中，则不操作【暂时不记录：因为太多了】
        for path in settings.API_OPERATION_EXCLUDE_START:
            if request.request_path.startswith(path):
                return
        info = {
            'request_username': user.username if isinstance(user, Users) else user['username'],
            'request_ip': getattr(request, 'request_ip', 'unknown'),
            'creator_id': user.id if isinstance(user, Users) else user['id'],
            'request_method': request.method,
            'request_path': request.request_path,
            'request_body': body,
            'response_code': response.data.get('code'),
            'request_os': get_os(request),
            'request_browser': get_browser(request),
            # 'request_msg': request.session.get('request_msg'),
            'status': True if response.data.get('code') in [200, ] else False,
            'json_result': {"code": response.data.get('code'), "msg": response.data.get('result')},
            # 接口所属模块直接落库（原实现用 update_or_create(id=None) 永远走新增分支）
            'request_modular': settings.API_MODEL_MAP.get(request.request_path, ''),
        }
        OperationLog.objects.create(**info)

    def process_request(self, request):
        self.__handle_request(request)

    def process_response(self, request, response):
        """
        主要请求处理完之后记录
        :param request:
        :param response:
        :return:
        """
        if self.enable:
            if self.methods == 'ALL' or request.method in self.methods:
                self.__handle_response(request, response)
        return response
