from ninja_extra import NinjaExtraAPI
from django.http import HttpRequest, HttpResponse
from typing import Any

# 重写ninja返回 - 全局
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
        if status != 200 and std_data['message'] == '请求成功':
            std_data['message'] = '请求失败，请检查'
        content = self.renderer.render(request, std_data, response_status=status)
        content_type = "{}; charset={}".format(
            self.renderer.media_type, self.renderer.charset
        )
        return HttpResponse(content, status=status, content_type=content_type)
