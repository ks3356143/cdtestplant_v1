from django.contrib.auth import get_user_model
from django.db import transaction
from django.shortcuts import get_object_or_404
from ninja_extra import api_controller, ControllerBase, route
from ninja_extra.permissions import IsAuthenticated
from ninja_jwt.authentication import JWTAuth

from apps.system.models import SecurityPolicy
from apps.system.schemas.policy import (ClearanceItemSchema, ClearanceUpdateSchema, SecurityPolicyOutSchema)
from apps.user.models import TableOperationLog
from utils.audit import audit_log, EVENT_CLEARANCE_CHANGE, EVENT_POLICY_CHANGE
from utils.chen_response import ChenResponse
from utils.permissions import IsSecurityAdmin

Users = get_user_model()

# 密级标记标签（与密级字典 secret 的 key 对应）
SECRET_LEVEL_LABELS = {'1': '公开', '2': '内部', '3': '秘密★5年', '4': '机密★10年', '5': '绝密★20年'}


# 安全策略接口：仅系统安全员（secadmin）可读写
@api_controller("/system/security", auth=JWTAuth(), permissions=[IsAuthenticated, IsSecurityAdmin],
                tags=['安全策略'])
class SecurityPolicyController(ControllerBase):
    """三权分立之系统安全员职责：登录失败锁定等安全策略的查看与配置、用户密级标记管理"""

    @route.get("/policy", response=SecurityPolicyOutSchema, url_name="security-policy-get")
    def get_policy(self):
        return SecurityPolicy.load()

    @route.put("/policy", response=SecurityPolicyOutSchema, url_name="security-policy-update")
    @transaction.atomic
    def update_policy(self, payload: SecurityPolicyOutSchema):
        policy = SecurityPolicy.load()
        old = {f: getattr(policy, f) for f in ('login_max_attempts', 'login_window_minutes', 'login_lock_minutes')}
        for field, value in payload.model_dump().items():
            setattr(policy, field, value)
        policy.save(update_fields=['login_max_attempts', 'login_window_minutes', 'login_lock_minutes',
                                   'update_datetime'])
        # 审计留痕（7.1.6：强制策略变更，新旧值对比）
        changed = {f: (old[f], getattr(policy, f)) for f in old if old[f] != getattr(policy, f)}
        detail = '安全策略变更：' + ('；'.join(f'{k}={v[0]}→{v[1]}' for k, v in changed.items())
                                  if changed else '无字段变化')
        audit_log(self.context.request, EVENT_POLICY_CHANGE, detail)
        return policy

    # ~~~~~~~~~~~~ 敏感标记管理（GB/T 28452-2012 7.1.4/7.1.5）：安全员负责为用户授予密级许可 ~~~~~~~~~~~~

    @route.get("/clearance/list", response=list[ClearanceItemSchema], url_name="clearance-list")
    def clearance_list(self):
        """全部用户的密级许可清单（安全员标记管理视图）"""
        return Users.objects.order_by('id')

    @route.put("/clearance/{user_id}", response=ClearanceItemSchema, url_name="clearance-update")
    @transaction.atomic
    def update_clearance(self, user_id: int, payload: ClearanceUpdateSchema):
        """为用户配置密级许可（主体的敏感标记）。唯一超级管理员账号不受标记管理约束"""
        user = get_object_or_404(Users, id=user_id)
        if user.username == 'superAdmin':
            return ChenResponse(code=400, status=400, message="系统管理员账号不参与密级标记管理")
        if user.clearance != payload.clearance:
            old_label = SECRET_LEVEL_LABELS.get(user.clearance, user.clearance)
            user.clearance = payload.clearance
            user.save(update_fields=['clearance', 'update_datetime'])
            new_label = SECRET_LEVEL_LABELS.get(payload.clearance, payload.clearance)
            # 审计留痕（7.1.6：敏感标记修改）+ 操作日志
            audit_log(self.context.request, EVENT_CLEARANCE_CHANGE,
                      f'敏感标记变更：用户 {user.username} 密级许可 {old_label} → {new_label}')
            TableOperationLog.objects.create(
                user=self.context.request.user,
                operate_obj=f'用户:{user.username}',
                operate_des=f'系统安全员将密级许可调整为{new_label}')
        return user
