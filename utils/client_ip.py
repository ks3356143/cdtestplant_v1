"""客户端 IP 提取（7.1.6 审计留痕 / 7.1.7 传输来源）。

只有请求确实来自受信反向代理（TRUSTED_PROXIES，默认本机）时才采信
X-Forwarded-For，且取最右侧地址（由最近的代理追加）；否则一律使用
REMOTE_ADDR，避免客户端伪造 XFF 污染审计记录。
"""
from django.conf import settings


def get_client_ip(request, default=''):
    if request is None:
        return default
    remote = (request.META.get('REMOTE_ADDR') or '').strip()
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR') or ''
    trusted = set(getattr(settings, 'TRUSTED_PROXIES', ('127.0.0.1', '::1')))
    if forwarded and remote and remote in trusted:
        parts = [p.strip() for p in forwarded.split(',') if p.strip()]
        if parts:
            return parts[-1]
    return remote or default
