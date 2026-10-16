from datetime import datetime
from typing import Optional

from ninja import ModelSchema, Field, Schema
from apps.system.models import AuditLog, LoginLog, OperationLog

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

# 5.统一审计日志输出schema（7.1.6）
class AuditLogOutSchema(Schema):
    id: int
    username: Optional[str] = None
    role: Optional[str] = None
    event_type: str
    detail: str
    success: bool
    ip: Optional[str] = None
    user_agent: Optional[str] = None
    create_datetime: datetime

# 6.统一审计日志检索过滤器（账号/时间/事件类型/告警/IP 多维度）
class AuditFilterSchema(Schema):
    username: Optional[str] = ''
    event_type: Optional[str] = ''
    ip: Optional[str] = ''
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    only_alerts: Optional[bool] = False
