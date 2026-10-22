from ninja_extra import NinjaExtraAPI
from django.http import HttpRequest, HttpResponse
from typing import Any
from utils.codes import HTTP_USER_PASSWORD_ERROR_CODE

# 重写ninja返回 - 全局统一视图函数返回，如果None则如下返回
class ChenNinjaAPI(NinjaExtraAPI):
    def create_response(
            self, request: HttpRequest, data: Any, *, status: int = 200, code: int = 200, message: str = "请求成功",
            temporal_response: HttpResponse = None,
    ) -> HttpResponse:
        std_data = {
            "code": code,
            "data": data,
            "message": message,
            # 统一响应：HTTP 状态或业务码非 200 即失败，前端可直接用 success 判断
            "success": status < 400 and code == 200
        }
        # 因为extra的APIException会添加到data['detail']里面的，所以做一致性处理转换
        if isinstance(std_data['data'], dict) and 'detail' in std_data['data']:
            std_data['message'] = std_data['data']['detail']
        # ~~~~~~~~~~正常异常,status进行通用处理:TODO:后续规划~~~~~~~~~~
        # 0.错误响应的业务码与 HTTP 状态保持一致（此前 403 响应体仍是 code=200，前端难以区分）
        if status >= 400 and code == 200:
            std_data['code'] = status
        # 1.当状态码为403时候：保留调用方给出的中文原因；空值或框架英文缺省文案改回中文
        if status == 403:
            msg = std_data['message'] or ''
            if (not msg) or msg == '请求成功' or msg.isascii():
                std_data['message'] = '您没有权限这样做'
        # 2.当状态码为401时候，根据APIException处理
        elif status == 401:
            detail = ''
            if isinstance(std_data['data'], dict):
                detail = str(std_data['data'].get('detail') or '')
            if detail in ('找不到指定凭据对应的有效用户',
                          'No active account found with the given credentials'):
                std_data['message'] = '账号或密码错误，如果是内网登录检查密码是否过期...'
                std_data['data']['code'] = HTTP_USER_PASSWORD_ERROR_CODE  # TODO:后续单独以枚举方式定义code
            elif detail:
                std_data['message'] = detail
                # 登录接口的验证码错误、账号锁定等业务失败也归入 40001，
                # 前端据此提示具体原因并留在登录页，而不是当成“登录状态过期”跳走
                if isinstance(std_data['data'], dict) and str(getattr(request, 'path', '')).endswith('/login'):
                    std_data['data']['code'] = HTTP_USER_PASSWORD_ERROR_CODE
            else:
                std_data['message'] = '身份认证失败或登录状态已失效，请重新登录'
        # 3.因为前端是获取message，所以这里处理（404/422 判断需排在通用失败分支之前，否则永远不可达）
        elif status == 404:
            std_data['message'] = '未找到相应的内容，请检查参数'
        elif status == 422:
            std_data['message'] = '请求的参数或响应数据未通过验证'
        elif status != 200 and std_data['message'] == '请求成功':
            std_data['message'] = '请求失败，请检查'
        content = self.renderer.render(request, std_data, response_status=status)
        content_type = "{}; charset={}".format(
            self.renderer.media_type, self.renderer.charset
        )
        return HttpResponse(content, status=status, content_type=content_type)
