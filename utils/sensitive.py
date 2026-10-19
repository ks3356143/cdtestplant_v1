# -*- coding: utf-8 -*-
"""
敏感信息脱敏 —— 支撑 GB/T 28452-2012 第三级 7.1.8「用户数据保密性保护」

用途：在把请求参数、异常信息、日志正文写入"动态记录介质"（接口操作日志表、
审计日志、日志文件）之前统一脱敏，避免用户口令、手机号、邮箱等敏感数据
被长期残留、被审计员以外的运维人员翻看。

规则：
- 口令/令牌类键：整体替换为等长 ``*``（保留长度便于排查"空口令"类问题）
- 手机号：保留前 3 后 4，中间打码（138****8888）
- 邮箱：保留首字符 + 域名（s***@example.com）
- 其余键原样保留；dict / list 递归处理，键名大小写不敏感
"""
import re

# 整体掩码的键（口令、令牌、验证码等——这些值本身就不能出现在任何记录里）
SECRET_KEYS = frozenset({
    'password', 'newpassword', 'oldpassword', 'newpassword_confirmation', 'confirmpassword',
    'passwd', 'pwd', 'token', 'access', 'refresh', 'secret', 'apikey', 'api_key',
    'captchacode', 'captcha_code', 'ldap_bind_password', 'authorization',
})

# 需要部分打码的键（保留可读性，仍能定位到人/设备）
PHONE_KEYS = frozenset({'phone', 'mobile', 'telephone', 'contact_phone', 'entrust_contact_phone',
                        'dev_contact_phone', 'test_contact_phone', 'phone_number'})
EMAIL_KEYS = frozenset({'email', 'mail', 'email_address'})

_PHONE_RE = re.compile(r'^(\d{3})\d{4}(\d{4})$')
_EMAIL_RE = re.compile(r'^(.)[^@]*(@.*)$')

MASK = '***'


def mask_secret(value):
    """口令类：等长星号；非字符串原样返回（数字/None 不该出现在这些键上）"""
    if isinstance(value, str):
        return '*' * len(value)
    return MASK


def mask_phone(value):
    """手机号：138****8888；非 11 位数字（座机/含分隔符）则保留首尾各 3 位"""
    if not isinstance(value, str) or value == '':
        return value
    clean = value.strip()
    m = _PHONE_RE.match(clean)
    if m:
        return f'{m.group(1)}****{m.group(2)}'
    if len(clean) <= 6:
        return '*' * len(clean)
    return f'{clean[:3]}****{clean[-3:]}'


def mask_email(value):
    """邮箱：s***@example.com；不含 @ 的按手机/账号规则处理"""
    if not isinstance(value, str) or value == '':
        return value
    m = _EMAIL_RE.match(value.strip())
    if m:
        return f'{m.group(1)}***{m.group(2)}'
    return mask_phone(value)


def mask_sensitive(data, _depth=0):
    """
    递归脱敏 dict / list。返回新对象，不改动入参（避免污染后续业务逻辑）。
    深度上限 6 层，防御异常数据结构导致的无限递归。
    """
    if _depth > 6:
        return data
    if isinstance(data, dict):
        out = {}
        for key, value in data.items():
            lowered = str(key).lower()
            if lowered in SECRET_KEYS:
                out[key] = mask_secret(value)
            elif lowered in PHONE_KEYS:
                out[key] = mask_phone(value)
            elif lowered in EMAIL_KEYS:
                out[key] = mask_email(value)
            else:
                out[key] = mask_sensitive(value, _depth + 1)
        return out
    if isinstance(data, list):
        return [mask_sensitive(item, _depth + 1) for item in data]
    if isinstance(data, tuple):
        return [mask_sensitive(item, _depth + 1) for item in data]
    return data
