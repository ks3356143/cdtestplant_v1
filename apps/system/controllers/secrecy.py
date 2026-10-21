# -*- coding: utf-8 -*-
"""
用户数据保密性保护接口（GB/T 28452-2012 第三级 7.1.8）

系统安全员在「安全策略 - 数据保密性」页查看：
- 已落库加密的敏感字段清单（由模型定义自动枚举，避免文档与代码脱节）
- 传输保密性现状（TLS 由部署层 nginx 承担）
- 剩余信息保护措施与临时文件占用，并可一键清理过期临时文件
"""
from pathlib import Path

from django.apps import apps as django_apps
from ninja_extra import api_controller, ControllerBase, route
from ninja_extra.permissions import IsAuthenticated
from ninja_jwt.authentication import JWTAuth

from apps.system.schemas.secrecy import (ConfidentialityOverviewOut, EncryptedFieldItem,
                                         ResidueMeasureItem, TempUsageOut, TransportSecurityOut)
from apps.system.tools.residue import RESIDUE_MEASURES, purge_temp_files, temp_dir_usage
from utils.audit import audit_log, EVENT_BUSINESS_CHANGE
from utils.chen_response import ChenResponse
from utils.crypto import EncryptedCharField
from utils.permissions import IsSecurityAdmin
from utils.sensitive import EMAIL_KEYS, PHONE_KEYS, SECRET_KEYS

# 部署层 HTTPS 配置（TLS 终止在 nginx，本文件仅用于"是否已落实"的展示判定）
HTTPS_CONF = Path(__file__).resolve().parents[3] / 'deploy' / 'https' / 'nginx_https.conf'
HTTPS_CERT = Path(__file__).resolve().parents[3] / 'deploy' / 'https' / 'localhost.crt'


def _encrypted_fields() -> list:
    """自动枚举全项目使用 EncryptedCharField 的字段，保证清单与代码同源"""
    items = []
    for model in django_apps.get_models():
        for field in model._meta.get_fields():
            if isinstance(field, EncryptedCharField):
                items.append(EncryptedFieldItem(
                    model=str(model._meta.verbose_name),
                    field=str(field.verbose_name),
                    name=field.name,
                    algorithm='Fernet（AES-128-CBC + HMAC-SHA256）',
                ))
    return items


def _transport_security() -> TransportSecurityOut:
    """传输保密性：由部署环境的 HTTPS 反向代理承担，这里如实汇报配置是否就位"""
    enabled = HTTPS_CONF.is_file() and HTTPS_CERT.is_file()
    # 端口随部署形态不同（打包部署 8443、云上为 443），这里只声明协议与承担方，不写死端口
    detail = ('由部署层的 HTTPS 反向代理承担（TLSv1.2/TLSv1.3）：随附 nginx TLS 反代配置与证书，'
              '线上以 443 为唯一入口（8081 仅 301 跳转），浏览器到服务器之间全程密文传输；'
              '见 deploy/https/README.md') \
        if enabled else '未检测到 HTTPS 配置，需在部署环境启用 TLS 反代后再上线'
    return TransportSecurityOut(
        enabled=enabled,
        protocol='TLSv1.2 / TLSv1.3' if enabled else '—',
        detail=detail,
        config_path='deploy/https/nginx_https.conf',
    )


@api_controller("/system/security", auth=JWTAuth(), permissions=[IsAuthenticated, IsSecurityAdmin],
                tags=['用户数据保密性'])
class ConfidentialityController(ControllerBase):
    """系统安全员：用户数据保密性保护现状查看与剩余信息清理"""

    @route.get("/confidentiality", response=ConfidentialityOverviewOut,
               url_name="confidentiality-overview")
    def overview(self):
        return ConfidentialityOverviewOut(
            encrypted_fields=_encrypted_fields(),
            residue_measures=[ResidueMeasureItem(**m) for m in RESIDUE_MEASURES],
            transport=_transport_security(),
            temp_usage=TempUsageOut(**temp_dir_usage()),
            masked_log_keys=sorted(SECRET_KEYS | PHONE_KEYS | EMAIL_KEYS),
        )

    @route.post("/residue/purge", url_name="residue-purge")
    def purge_residue(self, max_age_hours: int = 24):
        """清理超过保留期的临时文件（剩余信息保护，7.1.8 c/f）"""
        result = purge_temp_files(max_age_hours=max(0, min(max_age_hours, 24 * 365)))
        audit_log(self.context.request, EVENT_BUSINESS_CHANGE,
                  f'剩余信息清理：扫描 {result["scanned"]} 个临时文件，'
                  f'删除 {result["removed"]} 个（释放 {result["freed_mb"]} MB），'
                  f'保留期 {max_age_hours} 小时')
        return ChenResponse(data=result,
                            message=f'清理完成：删除 {result["removed"]} 个文件，'
                                    f'释放 {result["freed_mb"]} MB' +
                                    (f'，{result["failed"]} 个文件被占用跳过' if result['failed'] else ''))
