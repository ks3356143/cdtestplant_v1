from utils.chen_ninja import ChenNinjaAPI
from ninja.errors import HttpError
# 导入orjson解析器，渲染器，提升性能
from cdtestplant_v1.parser import MyParser
from cdtestplant_v1.renderer import MyRenderer
# swagger-ui配置
from ninja import Swagger
# 错误码
from utils.codes import PROJECT_ENDTIME_ERROR_CODE

api = ChenNinjaAPI(
    title="测试管理平台API",
    description="测试管理平台的接口一系列接口函数",
    urls_namespace="cdtestplant_v1",
    parser=MyParser(),
    renderer=MyRenderer(),
    docs=Swagger({"persistAuthorization": True})
)

# 捕获HttpError - 注意这种方式不过create_response函数，需自己定义
@api.exception_handler(HttpError)
def in_program_exception_handler(request, exc):
    # HttpError的status_code这里处理为自定义码，而非HTTP协议的
    data = {}
    if exc.status_code is PROJECT_ENDTIME_ERROR_CODE:
        data['flag'] = PROJECT_ENDTIME_ERROR_CODE
    return api.create_response(request, status=500, message=exc.message, data=data)

# 自动寻找每个app下面controllers.py中被@api_controller修饰的类
api.auto_discover_controllers()
