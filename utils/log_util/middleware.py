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

class ApiLoggingMiddleware(MiddlewareMixin):
    """
    用于记录API访问日志中间件
    """

    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.enable = getattr(settings, 'API_LOG_ENABLE', None) or False
        self.methods = getattr(settings, 'API_LOG_METHODS', None) or set()
        self.operation_log_id = None

    @classmethod
    def __handle_request(cls, request):
        request.request_ip = get_request_ip(request)
        request.request_data = get_request_data(request)
        request.request_path = get_request_path(request)

    def __handle_response(self, request, response):
        # request_data,request_ip由PermissionInterfaceMiddleware中间件中添加的属性
        body = getattr(request, 'request_data', {})
        # 请求含有password则用*替换掉(暂时先用于所有接口的password请求参数)
        if isinstance(body, dict) and body.get('password', ''):
            body['password'] = '*' * len(body['password'])
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
            'status': True if response.data.get('code') in [2000, ] else False,
            'json_result': {"code": response.data.get('code'), "msg": response.data.get('result')},
        }
        operation_log, creat = OperationLog.objects.update_or_create(defaults=info, id=self.operation_log_id)
        if not operation_log.request_modular and settings.API_MODEL_MAP.get(request.request_path, None):
            operation_log.request_modular = settings.API_MODEL_MAP[request.request_path]
            operation_log.save()

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
