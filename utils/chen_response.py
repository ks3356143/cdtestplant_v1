import json
import datetime
from django.http import HttpResponse

# 返回的时间有可能无法序列化，这里单独处理
class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime("%Y-%m-%d")
        else:
            return json.JSONEncoder.default(self, obj)

## 重写django的HttpResponse，注意返回的是axios里面的data!!!
class ChenResponse(HttpResponse):
    def __init__(self, data=None, message='success', code=200, *args, **kwargs):
        self.message = message
        if data is None:
            data = {}
        std_data = {
            "code": code,
            "data": data,
            "message": message,
            "success": True
        }
        data = json.dumps(std_data, cls=DateEncoder)
        super().__init__(data, *args, **kwargs)
