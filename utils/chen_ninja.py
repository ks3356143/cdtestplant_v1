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
            "success": True
        }
        # 因为extra的APIException会添加到data['detail']里面的，所以做一致性处理转换
        if std_data['data'] is not None:
            if 'detail' in std_data['data']:
                std_data['message'] = std_data['data']['detail']
        # ~~~~~~~~~~正常异常,status进行通用处理:TODO:后续规划~~~~~~~~~~
        # 1.当状态码为403时候，给前端提示message
        if status == 403:
            std_data['message'] = '您没有权限这样做'
        # 2.当状态码为401时候，根据APIException处理
        elif status == 401:
            if (std_data['data']['detail'] == '找不到指定凭据对应的有效用户' or
                    std_data['data']['detail'] == 'No active account found with the given credentials'):
                std_data['message'] = '账号或密码错误，如果是内网登录检查密码是否过期...'
                std_data['data']['code'] = HTTP_USER_PASSWORD_ERROR_CODE  # TODO:后续单独以枚举方式定义code
            else:
                std_data['message'] = '您的token已过期，请重新登录'
        # 3.因为前端是获取message，所以这里处理
        elif status != 200 and std_data['message'] == '请求成功':
            std_data['message'] = '请求失败，请检查'
        elif status == 404:
            std_data['message'] = '未找到相应的内容，请检查参数'
        elif status == 422:
            std_data['message'] = '请求的参数或响应数据未通过验证'
        content = self.renderer.render(request, std_data, response_status=status)
        content_type = "{}; charset={}".format(
            self.renderer.media_type, self.renderer.charset
        )
        return HttpResponse(content, status=status, content_type=content_type)
