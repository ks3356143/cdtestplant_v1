"""
角色权限类（三权分立支撑）
基于 ninja-extra 的 BasePermission，按 Users.role 字段判定：
- admin      系统管理员：用户与业务管理（不含审计日志）
- secadmin   系统安全员：安全策略配置（登录失败锁定等）
- auditadmin 系统审计员：各类日志审计
- user       普通业务用户
"""
from ninja_extra.permissions import BasePermission

# 角色取值约定（与前端 roles 路由配置保持一致）
ROLE_ADMIN = 'admin'
ROLE_SECADMIN = 'secadmin'
ROLE_AUDITADMIN = 'auditadmin'
ROLE_USER = 'user'

# 特权角色集合（三权）
PRIVILEGED_ROLES = (ROLE_ADMIN, ROLE_SECADMIN, ROLE_AUDITADMIN)


class RolePermission(BasePermission):
    """按角色判定的权限基类：allowed_roles 中的角色放行"""
    allowed_roles: tuple = ()

    def has_permission(self, request, controller):
        user = getattr(request, 'user', None)
        if user is None or not getattr(user, 'is_authenticated', False):
            return False
        return getattr(user, 'role', None) in self.allowed_roles


class IsAuditor(RolePermission):
    """系统审计员：日志监控类接口"""
    allowed_roles = (ROLE_AUDITADMIN,)


class IsSecurityAdmin(RolePermission):
    """系统安全员：安全策略类接口"""
    allowed_roles = (ROLE_SECADMIN,)


class IsSystemAdmin(RolePermission):
    """系统管理员"""
    allowed_roles = (ROLE_ADMIN,)
