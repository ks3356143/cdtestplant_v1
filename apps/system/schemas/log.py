from datetime import datetime
from typing import List, Optional

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

# 4.删除日志的Schema（day 不传时由后端取最小保留期默认值，前端不必硬编码）
class DeleteInputSchema(Schema):
    day: Optional[int] = Field(None, ge=0)

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
# 注意：start_time/end_time 为 None 时不参与过滤（controllers 中 if 真值判断保护）
class AuditFilterSchema(Schema):
    username: Optional[str] = ''
    event_type: Optional[str] = ''
    ip: Optional[str] = ''
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    only_alerts: Optional[bool] = False

# 7.数据完整性核查结果（7.1.7）
class IntegrityItemSchema(Schema):
    table: str
    id: int
    label: str
    ident: str
    algorithm: str
    stored: str
    actual: str
    intact: bool
    checked_at: Optional[datetime] = None

class IntegrityCheckOutSchema(Schema):
    total: int
    broken: int
    items: List[IntegrityItemSchema]
    recovery_hint: str
