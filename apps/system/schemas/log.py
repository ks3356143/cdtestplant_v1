from ninja import ModelSchema, Field, Schema
from apps.system.models import LoginLog, OperationLog

# 1.登录日志输出schema - 前五条
class LogOutSchema(ModelSchema):
    class Meta:
        model = LoginLog
        fields = ['id', 'username', 'agent', 'ip', 'browser', 'os', 'create_datetime']

# 2.操作日志输出shcema - 前五条
class OperationLogOutSchema(ModelSchema):
    class Meta:
        model = OperationLog
        exclude = ['remark', 'modifier', 'request_modular', 'request_msg', 'sort', 'creator']

# 3.登录日志输出schema
class LoginLogOutSchema(ModelSchema):
    class Meta:
        model = LoginLog
        exclude = ['remark', 'modifier', 'country', 'sort', 'creator']

# 4.删除日志的Schema
class DeleteInputSchema(Schema):
    day: int = Field(7, ge=0)
