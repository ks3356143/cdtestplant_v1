import os
from waitress import serve
from cdtestplant_v1.wsgi import application
# ~~~为了打包而添加~~~
import orjson

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cdtestplant_v1.settings')

# waitress-wsgi服务器
print('接口服务器启动完毕...')
serve(
    app=application,
    host='127.0.0.1',
    port=8000,
)
