from django.db import transaction
from ninja_extra import api_controller, ControllerBase, route
from ninja_extra.permissions import IsAuthenticated
from ninja_jwt.authentication import JWTAuth

from apps.system.models import SecurityPolicy
from apps.system.schemas.policy import SecurityPolicyOutSchema
from utils.permissions import IsSecurityAdmin


# 安全策略接口：仅系统安全员（secadmin）可读写
@api_controller("/system/security", auth=JWTAuth(), permissions=[IsAuthenticated, IsSecurityAdmin],
                tags=['安全策略'])
class SecurityPolicyController(ControllerBase):
    """三权分立之系统安全员职责：登录失败锁定等安全策略的查看与配置"""

    @route.get("/policy", response=SecurityPolicyOutSchema, url_name="security-policy-get")
    def get_policy(self):
        return SecurityPolicy.load()

    @route.put("/policy", response=SecurityPolicyOutSchema, url_name="security-policy-update")
    @transaction.atomic
    def update_policy(self, payload: SecurityPolicyOutSchema):
        policy = SecurityPolicy.load()
        for field, value in payload.model_dump().items():
            setattr(policy, field, value)
        policy.save(update_fields=['login_max_attempts', 'login_window_minutes', 'login_lock_minutes',
                                   'update_datetime'])
        return policy
