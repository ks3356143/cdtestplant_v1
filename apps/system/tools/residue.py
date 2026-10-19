# -*- coding: utf-8 -*-
"""
剩余信息保护（GB/T 28452-2012 第三级 7.1.8 c)/f)）

用户"释放对数据的使用权"（登出、关闭页面、生成任务结束）之后，及时清除
动态记录介质中残留的信息，避免被后续使用者读取：

1. **服务端临时缓存（Redis）**：按账号维度的登录失败计数、账号锁定标记等，
   登出时主动删除；未登出的键一律带 TTL（默认 5 分钟）自动过期。
2. **临时磁盘文件**：文档生成过程中的中间产物（``media/<R号>/temp``、
   ``media/<R号>/form_template/*/temporary``）在任务结束后已无用，
   按保留期清理；**输入模板与最终交付文档不在清理范围内**。
3. **内存缓冲区**：由 Python 运行时与操作系统负责回收（进程退出即释放），
   应用层不额外缓存敏感数据副本 —— 该层如实标注为"由运行环境承担"。
"""
import time
from pathlib import Path

from django.core.cache import cache

# 按账号维度的临时缓存键前缀（与 apps/user/tools/login_security.py 保持一致）
USER_TRANSIENT_PREFIXES = ('login_lock:', 'login_fail:')

# 临时文件目录（相对于 MEDIA_ROOT 的 glob），仅清理这些目录下的残留文件
TEMP_DIR_GLOBS = ('*/temp', '*/form_template/*/temporary')

# 剩余信息保护措施清单（安全策略页展示，供测评人员逐项核对）
RESIDUE_MEASURES = [
    {
        'name': '临时缓存键过期与主动清除',
        'detail': '登录失败计数/账号锁定等按账号维度的 Redis 键带 TTL（默认 5 分钟）'
                  '自动过期，登出时立即删除，不长期驻留。',
        'owner': '本平台（应用层）',
    },
    {
        'name': '临时文件按保留期清理',
        'detail': '文档生成中间产物落在 media/<R号>/temp 与 form_template/*/temporary，'
                  '保留期后清理；输入模板与最终交付文档不在清理范围。',
        'owner': '本平台（应用层）',
    },
    {
        'name': '日志中的敏感数据脱敏',
        'detail': '请求参数写入操作日志前统一脱敏：口令/令牌全掩码，手机号保留前 3 后 4，'
                  '邮箱保留首字符与域名（utils/sensitive.py）。',
        'owner': '本平台（应用层）',
    },
    {
        'name': '内存缓冲区与虚拟内存回收',
        'detail': '进程退出即释放内存；应用层不额外缓存敏感数据副本。'
                  '内存/交换分区的物理擦除由操作系统承担。',
        'owner': '操作系统（部署环境承担）',
    },
]


def clear_user_transient(username: str) -> int:
    """清除指定账号的服务端临时缓存键，返回清理条数（登出时调用）"""
    if not username:
        return 0
    cleared = 0
    for prefix in USER_TRANSIENT_PREFIXES:
        if cache.delete(f'{prefix}{username}'):
            cleared += 1
    return cleared


def _temp_roots():
    """
    临时文件根目录候选。

    文档生成代码统一写在项目根目录的 media/<R号>/ 下（见 createDocument 各控制器），
    而 settings.MEDIA_ROOT 指向部署包外的 uploads 目录，两者可能不一致，
    因此这里两个位置都扫，存在哪个就清哪个。
    """
    from django.conf import settings
    base = Path(getattr(settings, 'BASE_DIR', Path.cwd()))
    roots = [base / 'media', base / 'uploads']
    media_root = getattr(settings, 'MEDIA_ROOT', None)
    if media_root:
        roots.append(Path(media_root))
    seen, result = set(), []
    for root in roots:
        key = str(root.resolve()) if root.exists() else str(root)
        if key not in seen and root.is_dir():
            seen.add(key)
            result.append(root)
    return result


def _iter_temp_files():
    """遍历配置的临时目录下的所有普通文件"""
    for root in _temp_roots():
        for pattern in TEMP_DIR_GLOBS:
            for temp_dir in root.glob(pattern):
                if not temp_dir.is_dir():
                    continue
                for path in temp_dir.rglob('*'):
                    if path.is_file():
                        yield path


def temp_dir_usage() -> dict:
    """统计临时目录当前占用情况（供页面展示"剩余信息"现状）"""
    count = 0
    total = 0
    newest = 0.0
    for path in _iter_temp_files():
        try:
            stat = path.stat()
        except OSError:
            continue
        count += 1
        total += stat.st_size
        newest = max(newest, stat.st_mtime)
    return {
        'file_count': count,
        'total_bytes': total,
        'total_mb': round(total / 1024 / 1024, 2),
        'newest_mtime': newest,
    }


def purge_temp_files(max_age_hours: int = 24) -> dict:
    """
    清理超过保留期的临时文件。
    :param max_age_hours: 保留期（小时），默认 24；传 0 表示全部清理
    :return: {'scanned', 'removed', 'freed_bytes', 'freed_mb', 'failed'}
    """
    deadline = time.time() - max_age_hours * 3600
    scanned = removed = freed = failed = 0
    for path in _iter_temp_files():
        scanned += 1
        try:
            stat = path.stat()
        except OSError:
            failed += 1
            continue
        if max_age_hours > 0 and stat.st_mtime > deadline:
            continue
        try:
            size = stat.st_size
            path.unlink()
            removed += 1
            freed += size
        except OSError:
            # 文件正被占用（例如 Word 打开着生成的临时文档）：跳过，下次再清
            failed += 1
    return {
        'scanned': scanned,
        'removed': removed,
        'freed_bytes': freed,
        'freed_mb': round(freed / 1024 / 1024, 2),
        'failed': failed,
    }
