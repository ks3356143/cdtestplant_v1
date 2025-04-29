from utils.chen_ninja import ChenNinjaAPI
# 导入orjson解析器，渲染器，提升性能
from cdtestplant_v1.parser import MyParser
from cdtestplant_v1.renderer import MyRenderer
# swagger-ui配置
from ninja import Swagger

api = ChenNinjaAPI(
    title="测试管理平台API",
    description="测试管理平台的接口一系列接口函数",
    urls_namespace="cdtestplant_v1",
    parser=MyParser(),
    renderer=MyRenderer(),
    docs=Swagger({"persistAuthorization": True})
)

# 自动寻找每个app下面controllers.py中被@api_controller修饰的类
api.auto_discover_controllers()
