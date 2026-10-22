"""
登录鉴别失败处置（GB/T 28452-2012 第三级 7.1.1）
策略来源：系统安全策略表（系统安全员 secadmin 维护），Redis 计数/锁定。
在 MyTokenObtainPairInputSchema.authenticate() 中挂钩（认证发生在 pydantic 校验阶段）。
"""
import time

from ninja.errors import HttpError


def _login_lock_key(username: str) -> str:
    return f'login_lock:{username}'


def _login_fail_key(username: str) -> str:
    return f'login_fail:{username}'


def check_login_locked(username: str):
    """锁定中的账号拒绝登录，提示剩余时间"""
    from django.core.cache import cache
    lock_until = cache.get(_login_lock_key(username))
    if lock_until and time.time() < lock_until:
        remain = max(1, int((lock_until - time.time()) // 60) + 1)
        raise HttpError(401, f"账号已锁定（连续登录失败超限），约 {remain} 分钟后可重试")


def record_login_failure(username: str, request=None):
    """口令鉴别失败：窗口内累计，达到策略阈值锁定账号并告警（审计留痕 7.1.6，含 IP）"""
    from django.core.cache import cache
    from apps.system.models import LoginLog, SecurityPolicy
    from utils.audit import audit_log, EVENT_LOGIN_FAIL, EVENT_ACCOUNT_LOCK
    policy = SecurityPolicy.load()
    fail_key = _login_fail_key(username)
    fails = (cache.get(fail_key) or 0) + 1
    if fails >= policy.login_max_attempts:
        lock_seconds = policy.login_lock_minutes * 60
        cache.set(_login_lock_key(username), time.time() + lock_seconds, lock_seconds)
        cache.delete(fail_key)
        LoginLog.objects.create(username=username, remark='安全告警：连续登录失败超限，账号已锁定')
        audit_log(request, EVENT_ACCOUNT_LOCK,
                  f'安全告警：账号 {username} 连续登录失败 {fails} 次超限（{policy.login_max_attempts} 次阈值），已锁定 '
                  f'{policy.login_lock_minutes} 分钟', username=username, success=False)
    else:
        cache.set(fail_key, fails, policy.login_window_minutes * 60)
        audit_log(request, EVENT_LOGIN_FAIL,
                  f'账号 {username} 口令鉴别失败（第 {fails}/{policy.login_max_attempts} 次）', username=username, success=False)


def clear_login_failure(username: str):
    """登录成功清除失败计数"""
    from django.core.cache import cache
    cache.delete(_login_fail_key(username))
