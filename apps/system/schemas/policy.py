from typing import Annotated

from ninja import Field, Schema


class SecurityPolicyOutSchema(Schema):
    """系统安全策略（读取与更新共用）"""
    login_max_attempts: Annotated[int, Field(gt=0, le=100, description="登录失败最大尝试次数")]
    login_window_minutes: Annotated[int, Field(gt=0, le=1440, description="失败统计时间窗口（分钟）")]
    login_lock_minutes: Annotated[int, Field(gt=0, le=1440, description="账号锁定时长（分钟）")]


class ClearanceItemSchema(Schema):
    """用户敏感标记（密级许可）展示项"""
    id: int
    username: str
    name: str
    role: str = None
    clearance: str


class ClearanceUpdateSchema(Schema):
    """密级许可更新输入：1公开 < 2内部 < 3秘密★5年 < 4机密★10年 < 5绝密★20年"""
    clearance: Annotated[str, Field(pattern=r'^[1-5]$', description="密级字典 key（1-5）")]
