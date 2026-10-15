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
        raise HttpError(40001, f"账号已锁定（连续登录失败超限），约 {remain} 分钟后可重试")


def record_login_failure(username: str):
    """口令鉴别失败：窗口内累计，达到策略阈值锁定账号并写登录日志告警"""
    from django.core.cache import cache
    from apps.system.models import LoginLog, SecurityPolicy
    policy = SecurityPolicy.load()
    fail_key = _login_fail_key(username)
    fails = (cache.get(fail_key) or 0) + 1
    if fails >= policy.login_max_attempts:
        lock_seconds = policy.login_lock_minutes * 60
        cache.set(_login_lock_key(username), time.time() + lock_seconds, lock_seconds)
        cache.delete(fail_key)
        # 安全告警：写入登录日志，供审计员追溯
        LoginLog.objects.create(username=username, remark='安全告警：连续登录失败超限，账号已锁定')
    else:
        cache.set(fail_key, fails, policy.login_window_minutes * 60)


def clear_login_failure(username: str):
    """登录成功清除失败计数"""
    from django.core.cache import cache
    cache.delete(_login_fail_key(username))
