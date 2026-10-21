import os
from waitress import serve
from cdtestplant_v1.wsgi import application
# ~~~为了打包而添加~~~
import orjson

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cdtestplant_v1.settings')

# 反向代理（nginx）跑在本机回环，只信任它送来的转发头。
# 注意：不配置 trusted_proxy 时 waitress 默认会清除 X-Forwarded-* 头（clear_untrusted），
# 审计日志就只能记到 127.0.0.1 —— GB/T 28452-2012 7.1.6 要求如实记录来源 IP，
# 这里让 waitress 采信本机代理的 X-Forwarded-For，并把真实客户端 IP 写回 REMOTE_ADDR。
TRUSTED_PROXY = os.environ.get('WAITRESS_TRUSTED_PROXY', '127.0.0.1')

# waitress-wsgi服务器
print('接口服务器启动完毕...')
serve(
    app=application,
    host='127.0.0.1',
    port=8000,
    trusted_proxy=TRUSTED_PROXY,
    trusted_proxy_count=1,
    trusted_proxy_headers={'x-forwarded-for', 'x-forwarded-proto', 'x-forwarded-host'},
)
