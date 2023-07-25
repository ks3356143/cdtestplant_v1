from utils.chen_ninja import ChenNinjaAPI
from utils.chen_response import ChenResponse
from ninja.errors import ValidationError

api = ChenNinjaAPI(
    title="成都测试平台API",
    description="成都测试平台的接口一系列接口函数",
    urls_namespace="cdtestplant_v1",
)

# 统一处理server异常
# @api.exception_handler(Exception)
# def a(request, exc):
#     if hasattr(exc, 'errno'):
#         return api.create_response(request, data=[], message=str(exc), code=exc.errno)
#     else:
#         return api.create_response(request, data=[], message=str(exc), code=500)

# 字段重复-注意一旦这样，那所有ValidationError全变成这个了，注意
# @api.exception_handler(ValidationError)
# def validation_errors(request, exc):
#     return ChenResponse(message="唯一标识或名字重复错误", status=400,code=400)

api.auto_discover_controllers()