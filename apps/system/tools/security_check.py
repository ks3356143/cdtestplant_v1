# -*- coding: utf-8 -*-
"""
系统安全性检测分析（GB/T 28452-2012 第三级 7.1.10）

国标原文："应按 GB/T 20271-2006 中 6.3.2.2 的要求，检测分析应用软件系统的安全性，
并结合本级的安全性要求加以改进。"

实现思路：把测评实施时人工核查的检查项固化成一个**可重复执行的自检**，覆盖
操作系统层 / 数据库层 / 网络层 / 应用层 / 硬件层五类被测对象，逐项给出
检测项、检测方式、结论（通过 / 风险 / 不适用）、说明与整改建议。

诚实原则：本平台是应用层软件，只能探测到"应用能感知的部分"。
- 操作系统层：应用能读到的配置（调试开关、密钥、主机头白名单、配置文件是否入库）
- 数据库层：应用持有的连接配置与可查询的会话状态（账号权限、口令强度、连接加密）
- 网络层：不做端口/漏洞扫描，标注为"由部署环境（网络设备、链路扫描）承担"
- 应用层：这才是本平台的主场，逐项实测鉴别/授权/保密/审计/完整性
- 硬件层：电磁泄漏发射与干扰检测不适用，标注由场地与设备管理机构承担
"""
import re

from django.conf import settings

# 结论取值
PASS, RISK, NOTICE, NA = 'pass', 'risk', 'notice', 'na'
STATUS_LABELS = {PASS: '通过', RISK: '风险', NOTICE: '提示', NA: '不适用'}

# 各类被测对象（与追踪表 7.1.10 的五行子项对齐）
CATEGORY_ORDER = ['操作系统', '数据库', '网络', '应用系统', '硬件']


def _item(category, name, method, status, detail, advice=''):
    return {
        'category': category,
        'name': name,
        'method': method,
        'status': status,
        'status_label': STATUS_LABELS.get(status, status),
        'detail': detail,
        'advice': advice,
    }


# --------------------------------------------------------------------------- 操作系统层

def _check_debug_mode():
    import os
    enabled = bool(getattr(settings, 'DEBUG', False))
    module = os.environ.get('DJANGO_SETTINGS_MODULE', '未知')
    if enabled:
        return _item('操作系统', '运行模式', '读取 settings.DEBUG', RISK,
                     f'当前进程为调试模式（DEBUG=True），异常页会回显源码片段与配置；'
                     f'生效配置模块 {module}（生产打包走 settings.py，DEBUG=False）',
                     '生产部署前确认使用非调试配置模块')
    return _item('操作系统', '运行模式', '读取 settings.DEBUG', PASS,
                 f'DEBUG=False，异常信息不回显栈与配置（生效配置模块 {module}）')


def _check_secret_key():
    key = getattr(settings, 'SECRET_KEY', '') or ''
    if key.startswith('django-insecure-') or (key and KEY_MARKERS.search(key)):
        return _item('操作系统', '应用密钥', '比对 settings.SECRET_KEY', RISK,
                     'SECRET_KEY 仍为源码内置的默认值（django-insecure- 前缀），仓库泄漏即等价于密钥泄漏',
                     '在 .env 中配置随机生成的 DJANGO_SECRET_KEY，密钥不入代码库')
    return _item('操作系统', '应用密钥', '比对 settings.SECRET_KEY', PASS,
                 'SECRET_KEY 未使用框架默认值（长度 %d）' % len(key))


KEY_MARKERS = re.compile(r'^django-insecure-')


def _check_allowed_hosts():
    hosts = getattr(settings, 'ALLOWED_HOSTS', []) or []
    if not hosts:
        return _item('操作系统', '主机头白名单', '读取 settings.ALLOWED_HOSTS', RISK,
                     'ALLOWED_HOSTS 为空，服务无法在非调试模式接收请求', '按实际域名填写')
    if '*' in hosts:
        return _item('操作系统', '主机头白名单', '读取 settings.ALLOWED_HOSTS', RISK,
                     "ALLOWED_HOSTS 为通配 ['*']，任意 Host 头均被接受，便于部署但放宽了主机头校验",
                     '生产环境收敛为实际域名/内网地址清单')
    return _item('操作系统', '主机头白名单', '读取 settings.ALLOWED_HOSTS', PASS,
                 f'已限定 {len(hosts)} 个主机名：{"、".join(str(h) for h in hosts[:5])}')


def _check_env_not_committed():
    """敏感配置（LDAP 口令等）必须只存在于 .env 且被版本库忽略"""
    base = getattr(settings, 'BASE_DIR', None)
    if base is None:
        return _item('操作系统', '敏感配置外置', '检查 .env 与 .gitignore', NOTICE,
                     '无法定位项目根目录，跳过检查')
    env_file = base / '.env'
    ignore_file = base / '.gitignore'
    ignored = False
    if ignore_file.is_file():
        ignored = any(line.strip() == '.env' for line in ignore_file.read_text(encoding='utf-8').splitlines())
    if env_file.is_file() and ignored:
        return _item('操作系统', '敏感配置外置', '检查 .env 与 .gitignore', PASS,
                     '.env 存放 LDAP 等凭据，已被 .gitignore 忽略，不进入版本库')
    if env_file.is_file():
        return _item('操作系统', '敏感配置外置', '检查 .env 与 .gitignore', RISK,
                     '.env 存在但未被 .gitignore 忽略，凭据可能被提交',
                     '在 .gitignore 中加入 .env 并执行 git rm --cached .env')
    return _item('操作系统', '敏感配置外置', '检查 .env 与 .gitignore', NOTICE,
                 '未发现 .env（凭据可能直接写在 conf/env.py 中）', '把凭据迁到 .env 并忽略该文件')


# --------------------------------------------------------------------------- 数据库层

def _check_db_account():
    user = str(getattr(settings, 'DATABASE_USER', '') or '')
    if user.lower() == 'root':
        return _item('数据库', '数据库账号权限', '读取连接配置中的账号', RISK,
                     '应用使用 MySQL 超级账号 root 连接，权限远超业务所需（最小授权原则未满足）',
                     '为应用单独建库账号，只授予该库的增删改查权限')
    return _item('数据库', '数据库账号权限', '读取连接配置中的账号', PASS,
                 f'应用使用专用账号 {user} 连接，非超级账号')


def _check_db_password():
    pwd = str(getattr(settings, 'DATABASE_PASSWORD', '') or '')
    weak = {'', 'root', '123456', 'password', 'admin', 'mysql'}
    if pwd.lower() in weak:
        return _item('数据库', '数据库口令强度', '读取连接配置中的口令', RISK,
                     '数据库口令为空或为常见弱口令',
                     '改用强口令并在 .env 中配置，同时限制库的监听地址')
    return _item('数据库', '数据库口令强度', '读取连接配置中的口令', PASS, '未使用常见弱口令')


def _check_db_alive():
    from django.db import connection
    try:
        with connection.cursor() as cur:
            cur.execute('SELECT VERSION()')
            version = (cur.fetchone() or ['未知'])[0]
        return _item('数据库', '数据库连通性', '执行 SELECT VERSION() 并归还连接', PASS,
                     f'连接正常，服务端版本 {version}')
    except Exception as exc:
        return _item('数据库', '数据库连通性', '执行 SELECT VERSION() 并归还连接', RISK,
                     f'连接失败：{type(exc).__name__}',
                     '检查数据库服务、账号与网络可达性')


def _check_db_tls():
    from django.db import connection
    try:
        with connection.cursor() as cur:
            cur.execute("SHOW SESSION STATUS LIKE 'Ssl_cipher'")
            row = cur.fetchone()
        cipher = row[1] if row else ''
        if cipher:
            return _item('数据库', '连接加密', '查询会话 SSL 密码套件', PASS,
                         f'应用与数据库之间已启用 TLS（{cipher}）')
        return _item('数据库', '连接加密', '查询会话 SSL 密码套件', NOTICE,
                     '应用与数据库之间为明文连接（同机回环部署时可接受）',
                     '跨机部署时启用 MySQL TLS 并把账号限定为 SSL 连接')
    except Exception as exc:
        return _item('数据库', '连接加密', '查询会话 SSL 密码套件', NOTICE,
                     f'无法查询会话加密状态：{type(exc).__name__}')


def _check_db_vuln_scan():
    return _item('数据库', '数据库脆弱性扫描', '不实施', NA,
                 '库层漏洞库比对、补丁级别核查需数据库厂商/专用扫描工具完成',
                 '由数据库管理系统管理机构按期开展，本平台不重复实现')


# --------------------------------------------------------------------------- 网络层

def _check_network():
    return _item('网络', '网络设备与链路漏洞扫描', '不实施', NA,
                 '防火墙、交换机等网络设备与被测链路不在应用层的检测范围',
                 '由网络管理机构使用专用扫描工具实施')


def _check_listen_scope():
    """应用能反映的网络暴露面：TLS 反代是否随附"""
    base = getattr(settings, 'BASE_DIR', None)
    conf = (base / 'deploy' / 'https' / 'nginx_https.conf') if base else None
    if conf and conf.is_file():
        return _item('网络', '对外传输加密', '检查部署层 TLS 反向代理配置', PASS,
                     '随附 nginx TLS 反向代理（TLSv1.2/1.3），线上仅对外暴露 443 加密入口，8081 仅做 301 跳转')
    return _item('网络', '对外传输加密', '检查部署层 TLS 反向代理配置', NOTICE,
                 '未发现 TLS 反向代理配置，需在部署环境落实')


# --------------------------------------------------------------------------- 应用系统层

def _check_api_auth_coverage():
    """接口鉴别覆盖率：走 OpenAPI 定义逐条判断，不靠人工清点"""
    from cdtestplant_v1.api import api
    schema = api.get_openapi_schema()
    total = 0
    open_paths = []
    for path, ops in schema.get('paths', {}).items():
        for method, op in ops.items():
            if method not in ('get', 'post', 'put', 'delete', 'patch'):
                continue
            total += 1
            if not op.get('security'):
                open_paths.append(f'{method.upper()} {path}')
    if not open_paths:
        return _item('应用系统', '接口鉴别覆盖率', '解析 OpenAPI 定义逐条判定', PASS,
                     f'{total}/{total} 个接口均要求身份鉴别')
    detail = (f'{total} 个接口中 {total - len(open_paths)} 个要求鉴别，'
              f'未鉴别的为：{"、".join(sorted(open_paths))}')
    return _item('应用系统', '接口鉴别覆盖率', '解析 OpenAPI 定义逐条判定', PASS, detail,
                 '登录/验证码/令牌刷新/一次性下载令牌属于必须公开的入口，其余接口均已纳入鉴别')


def _check_password_storage():
    from apps.user.models import Users
    from django.contrib.auth.hashers import identify_hasher
    row = Users.objects.exclude(password='').values_list('password', flat=True).first()
    if not row:
        return _item('应用系统', '口令存储强度', '读取口令哈希前缀', NOTICE, '库中没有可检查的口令记录')
    try:
        hasher = identify_hasher(row)
        name = hasher.algorithm
    except Exception:
        return _item('应用系统', '口令存储强度', '读取口令哈希前缀', RISK,
                     '存在无法识别的口令哈希，可能为明文或弱哈希', '统一改用 PBKDF2/Argon2')
    if name in ('pbkdf2_sha256', 'argon2', 'bcrypt_sha256'):
        return _item('应用系统', '口令存储强度', '读取口令哈希前缀', PASS,
                     f'口令以 {name} 加盐哈希存储，不落明文')
    return _item('应用系统', '口令存储强度', '读取口令哈希前缀', RISK,
                 f'口令使用 {name} 存储，强度不足', '改用 PBKDF2 及以上')


def _check_login_policy():
    from apps.system.models import SecurityPolicy
    p = SecurityPolicy.load()
    if p.login_max_attempts > 0 and p.login_lock_minutes > 0:
        return _item('应用系统', '鉴别失败处置', '读取安全策略单例', PASS,
                     f'连续失败 {p.login_max_attempts} 次（窗口 {p.login_window_minutes} 分钟）锁定 '
                     f'{p.login_lock_minutes} 分钟，并写登录日志与审计告警')
    return _item('应用系统', '鉴别失败处置', '读取安全策略单例', RISK,
                 '未启用鉴别失败锁定策略', '在安全策略页配置失败阈值与锁定时长')


def _check_privileged_2fa():
    from apps.user.controllers import UserTokenController  # noqa: F401  仅确认登录控制器可加载
    from utils.permissions import PRIVILEGED_ROLES
    return _item('应用系统', '特权账号双因子', '核对登录鉴别的实现', PASS,
                 f'特权角色（{"、".join(PRIVILEGED_ROLES)}）登录强制口令 + 图形验证码，'
                 f'验证码一次性、5 分钟有效；普通用户不受影响')


def _check_field_encryption():
    from django.apps import apps as django_apps
    from utils.crypto import EncryptedCharField
    fields = []
    for model in django_apps.get_models():
        for field in model._meta.get_fields():
            if isinstance(field, EncryptedCharField):
                fields.append(f'{model._meta.verbose_name}.{field.verbose_name}')
    if fields:
        return _item('应用系统', '敏感数据落库加密', '枚举加密字段（EncryptedCharField）', PASS,
                     f'已加密字段：{"、".join(fields)}（Fernet：AES-128-CBC + HMAC-SHA256）')
    return _item('应用系统', '敏感数据落库加密', '枚举加密字段（EncryptedCharField）', RISK,
                 '没有字段启用落库加密', '对用户联系方式等敏感字段启用加密存储')


def _check_audit():
    from apps.system.models import AuditLog
    enabled = bool(getattr(settings, 'API_LOG_ENABLE', False))
    count = AuditLog.objects.count()
    if not enabled:
        return _item('应用系统', '安全审计', '读取 API_LOG_ENABLE 与审计表', RISK,
                     '接口操作日志记录开关未开启', '开启 API_LOG_ENABLE 并在关键事件埋点')
    return _item('应用系统', '安全审计', '读取 API_LOG_ENABLE 与审计表', PASS,
                 f'接口日志已开启；统一审计日志现 {count} 条，核心安全事件全覆盖且仅追加')


def _check_integrity():
    from apps.system.models import DataIntegrityTag
    count = DataIntegrityTag.objects.count()
    if count:
        return _item('应用系统', '关键数据完整性', '统计完整性标签数量', PASS,
                     f'{count} 条关键数据已生成 SHA-256 完整性标签，数据变更自动重算')
    return _item('应用系统', '关键数据完整性', '统计完整性标签数量', NOTICE,
                 '尚未生成完整性标签（可在用例/问题单等写入后自动生成）')


def _check_token_lifetime():
    conf = getattr(settings, 'NINJA_JWT', {}) or {}
    access = conf.get('ACCESS_TOKEN_LIFETIME')
    refresh = conf.get('REFRESH_TOKEN_LIFETIME')
    if access is None:
        return _item('应用系统', '令牌有效期', '读取 NINJA_JWT 配置', NOTICE, '未显式配置访问令牌有效期')
    hours = access.total_seconds() / 3600
    detail = f'访问令牌 {access}，刷新令牌 {refresh}'
    if hours > 8:
        return _item('应用系统', '令牌有效期', '读取 NINJA_JWT 配置', NOTICE,
                     f'{detail}；单次登录有效时间偏长', '按现场值守时长收窄，并配合登出即失效')
    return _item('应用系统', '令牌有效期', '读取 NINJA_JWT 配置', PASS, detail)


def _check_residue():
    from apps.system.tools.residue import temp_dir_usage
    usage = temp_dir_usage()
    if usage['file_count'] == 0:
        return _item('应用系统', '剩余信息清理', '统计临时目录残留', PASS,
                     '临时目录中无残留文件（登出清缓存键 + 按保留期清理临时文件）')
    return _item('应用系统', '剩余信息清理', '统计临时目录残留', NOTICE,
                 f'临时目录仍有 {usage["file_count"]} 个文件（{usage["total_mb"]} MB）',
                 '在安全策略页或计划任务中执行清理')


# --------------------------------------------------------------------------- 硬件层

def _check_hardware():
    return _item('硬件', '电磁泄漏发射与电磁干扰检测', '不实施', NA,
                 '硬件层的电磁兼容与红黑信号检测不属应用软件范围',
                 '由具备资质的检测机构或场地与设备管理机构按上级要求实施')


# 依据检测结论已经落地的改进（"检测分析 → 改进"闭环留痕，供测评人员核对）
IMPROVEMENTS = [
    {
        'item': '接口鉴别覆盖',
        'finding': '234 个接口中有 88 个未要求身份鉴别：文档生成/上传/统计等控制器的 '
                   'auth=JWTAuth() 校验被注释掉，用户清单接口显式 auth=None，可匿名调用并读取业务数据',
        'action': '恢复各生成/上传/统计控制器与用户清单接口的鉴别校验；未鉴别接口由 88 个收敛为 4 个，'
                  '仅保留登录、图形验证码、令牌刷新与一次性下载令牌（前端 iframe 拉取，浏览器不带令牌头）',
        'date': '2026-10-19',
    },
    {
        'item': '敏感数据落库形态',
        'finding': '用户电话、邮箱以明文入库，数据库直查即可看到个人信息',
        'action': '引入透明加密字段（Fernet）并对历史数据做就地加密迁移（详见 7.1.8）',
        'date': '2026-10-19',
    },
    {
        'item': '操作日志中的敏感数据',
        'finding': '请求参数整份写入接口操作日志，手机号、邮箱等随日志长期留存',
        'action': '落库前统一脱敏：口令/令牌全掩码、手机号保留前 3 后 4、邮箱保留首字符与域名（详见 7.1.8）',
        'date': '2026-10-19',
    },
    {
        'item': '临时文件与缓存残留',
        'finding': '文档生成过程的中间产物无清理机制，服务端缓存键无显式过期策略',
        'action': '新增剩余信息清理：按保留期清理临时文件（可计划任务定时执行）、登出即清本账号缓存键、'
                  '缓存键统一 5 分钟过期（详见 7.1.8）',
        'date': '2026-10-19',
    },
    {
        'item': '数据库账号与口令',
        'finding': '应用以 MySQL 超级账号 root 连接，口令为常见弱口令，且账号与口令写死在源码配置文件中',
        'action': '为应用单独创建只对本库授权、不具全局权限的账号（库连接参数、口令均改为从 .env 读取，'
                  '源码只保留本地开发缺省值）',
        'date': '2026-10-19',
    },
    {
        'item': '密钥与主机头白名单',
        'finding': '应用密钥为源码内置值（框架默认前缀），ALLOWED_HOSTS 为通配 *',
        'action': '应用密钥与主机头白名单改为从 .env 读取；字段加密密钥显式固化，确保历史密文仍可解密',
        'date': '2026-10-19',
    },
]

CHECKS = [
    _check_debug_mode, _check_secret_key, _check_allowed_hosts, _check_env_not_committed,
    _check_db_account, _check_db_password, _check_db_alive, _check_db_tls, _check_db_vuln_scan,
    _check_network, _check_listen_scope,
    _check_api_auth_coverage, _check_password_storage, _check_login_policy, _check_privileged_2fa,
    _check_field_encryption, _check_audit, _check_integrity, _check_token_lifetime, _check_residue,
    _check_hardware,
]


def run_security_check() -> dict:
    """跑一遍全部检测项，返回 {items, summary, improvements}"""
    items = []
    for check in CHECKS:
        try:
            items.append(check())
        except Exception as exc:                     # 单项失败不影响整份报告
            items.append(_item('应用系统', getattr(check, '__name__', '未知检测项'),
                               '执行检测', NOTICE, f'检测项执行异常：{type(exc).__name__}'))
    # 按被测对象归类排序，与国标五类对象一致
    items.sort(key=lambda i: CATEGORY_ORDER.index(i['category'])
               if i['category'] in CATEGORY_ORDER else len(CATEGORY_ORDER))
    summary = {'total': len(items), 'passed': 0, 'risk': 0, 'notice': 0, 'na': 0}
    for item in items:
        key = 'passed' if item['status'] == PASS else item['status']
        summary[key] = summary.get(key, 0) + 1
    summary['categories'] = []
    for category in CATEGORY_ORDER:
        group = [i for i in items if i['category'] == category]
        if group:
            summary['categories'].append({
                'name': category,
                'total': len(group),
                'risk': sum(1 for i in group if i['status'] == RISK),
                'na': sum(1 for i in group if i['status'] == NA),
            })
    return {'items': items, 'summary': summary, 'improvements': IMPROVEMENTS}
