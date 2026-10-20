"""受保护的本地媒体文件访问（/uploads/*）。

历史实现直接使用 django.views.static.serve，任何拿到 URL 的人都能匿名下载 uploads 下的文件。
现在要求请求携带有效 JWT（Authorization: Bearer 或 ?token=），校验通过才交给静态视图；
文档预览/下载仍走一次性下载令牌接口，不受影响。
"""
from django.conf import settings
from django.http import HttpResponseForbidden
from django.views.static import serve
from ninja_jwt.tokens import AccessToken


def _extract_token(request):
    auth = request.META.get('HTTP_AUTHORIZATION', '')
    if auth.lower().startswith('bearer '):
        return auth[7:].strip()
    return (request.GET.get('token') or '').strip()


def protected_media(request, path):
    token = _extract_token(request)
    if not token:
        return HttpResponseForbidden('需要登录后才能访问该文件')
    try:
        AccessToken(token)
    except Exception:
        return HttpResponseForbidden('登录凭证无效或已过期')
    return serve(request, path, document_root=settings.MEDIA_ROOT)
