from typing import Annotated

from ninja import Field, Schema


class SecurityPolicyOutSchema(Schema):
    """系统安全策略（读取与更新共用）"""
    login_max_attempts: Annotated[int, Field(gt=0, le=100, description="登录失败最大尝试次数")]
    login_window_minutes: Annotated[int, Field(gt=0, le=1440, description="失败统计时间窗口（分钟）")]
    login_lock_minutes: Annotated[int, Field(gt=0, le=1440, description="账号锁定时长（分钟）")]
