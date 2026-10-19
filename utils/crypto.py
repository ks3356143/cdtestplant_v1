# -*- coding: utf-8 -*-
"""
字段级加密工具 —— 支撑 GB/T 28452-2012 第三级 7.1.8「用户数据保密性保护」

设计要点：
1. 用户重要数据（电话、邮箱等个人敏感信息）落库前加密，数据库管理员直接查表
   只能看到密文（形如 ``enc:v1:gAAAAA...``），满足"存储保密性"。
2. 算法采用 Fernet（AES-128-CBC 加密 + HMAC-SHA256 认证），具备完整性校验，
   密文被篡改时解密直接失败，不会静默返回错误数据。
3. 密钥优先取环境变量 ``FIELD_ENCRYPTION_KEY``；未配置时由 ``SECRET_KEY``
   派生，保证开箱即用。**生产环境必须显式配置固定密钥**：密钥一旦变更，
   历史密文将无法解密（见 SRS 追踪表 7.1.8 说明）。
4. 兼容历史明文：非 ``enc:`` 前缀的值按明文原样返回，记录下次保存时自动加密，
   因此本模块可平滑上线，不需要停机改数据。
5. 加密后无法做 SQL 模糊匹配，故提供 ``blind_index()`` 盲索引（SHA-256），
   用于需要等值检索的字段（如按电话精确查找用户）。
"""
import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken
from django.db import models

# 密文前缀，同时作为版本标记：将来更换算法可升级为 enc:v2:
ENCRYPTED_PREFIX = 'enc:v1:'

_fernet_cache = None


def _build_key(seed: str) -> bytes:
    """把任意长度的种子串规整为 Fernet 要求的 32 字节 urlsafe base64 密钥"""
    digest = hashlib.sha256(seed.encode('utf-8')).digest()
    return base64.urlsafe_b64encode(digest)


def get_fernet() -> Fernet:
    """取 Fernet 实例（进程内缓存，避免每次加解密都派生密钥）"""
    global _fernet_cache
    if _fernet_cache is None:
        from django.conf import settings
        seed = getattr(settings, 'FIELD_ENCRYPTION_KEY', '') or settings.SECRET_KEY
        _fernet_cache = Fernet(_build_key(seed))
    return _fernet_cache


def is_encrypted(value) -> bool:
    """判断一个值是否已是本模块产出的密文"""
    return isinstance(value, str) and value.startswith(ENCRYPTED_PREFIX)


def encrypt_value(value):
    """加密明文；空值、非字符串、已加密的值原样返回（幂等）"""
    if value is None or not isinstance(value, str) or value == '' or is_encrypted(value):
        return value
    token = get_fernet().encrypt(value.encode('utf-8')).decode('ascii')
    return ENCRYPTED_PREFIX + token


def decrypt_value(value):
    """解密密文；明文或解不开的值原样返回（历史数据/密钥变更时不至于整页报错）"""
    if not is_encrypted(value):
        return value
    try:
        return get_fernet().decrypt(value[len(ENCRYPTED_PREFIX):].encode('ascii')).decode('utf-8')
    except (InvalidToken, ValueError):
        # 密钥不一致或密文被篡改：返回占位串而非抛异常，避免拖垮列表接口
        return '<解密失败>'


def blind_index(value) -> str:
    """等值检索用的盲索引：SHA-256 十六进制串，空值返回空串"""
    if value is None or value == '':
        return ''
    return hashlib.sha256(str(value).strip().encode('utf-8')).hexdigest()


class EncryptedCharField(models.CharField):
    """
    透明加密的字符字段：写库自动加密、读库自动解密，业务代码无感知。

    - ``get_prep_value``：Django 把 Python 值转成数据库值时调用（save/update/bulk_create 均经过）
    - ``from_db_value``：从数据库取回值时调用（含 values()/values_list()）
    """

    description = '透明加密存储的字符字段（GB/T 28452-2012 7.1.8）'

    def get_prep_value(self, value):
        return encrypt_value(super().get_prep_value(value))

    def from_db_value(self, value, expression, connection):
        return decrypt_value(value)
