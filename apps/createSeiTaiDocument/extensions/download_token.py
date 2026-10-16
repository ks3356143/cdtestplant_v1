# -*- coding: utf-8 -*-
"""
文档一次性下载令牌（应用文档生成 → 二段式下载）
令牌存 Redis（10 分钟有效、一次性使用），兼容多进程部署；取用时惰性清理，无常驻线程。
"""
import uuid

from django.core.cache import cache

TOKEN_EXPIRE = 600  # 令牌有效期（秒）
KEY_PREFIX = 'dl_token:'


def generate_download_token(file_path) -> str:
    """生成一次性下载令牌：token -> 文件路径（Redis，10 分钟）"""
    token = uuid.uuid4().hex
    cache.set(f'{KEY_PREFIX}{token}', str(file_path), TOKEN_EXPIRE)
    return token


def get_file_by_token(token: str):
    """根据令牌取文件路径；已使用/过期即失效（一次性下载），惰性清理"""
    key = f'{KEY_PREFIX}{token}'
    file_path = cache.get(key)
    if not file_path:
        return None
    cache.delete(key)  # 一次性使用
    from pathlib import Path
    return Path(file_path)
