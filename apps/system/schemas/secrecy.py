# -*- coding: utf-8 -*-
"""用户数据保密性保护（GB/T 28452-2012 第三级 7.1.8）相关 Schema"""
from typing import List

from ninja import Schema


class EncryptedFieldItem(Schema):
    """落库加密的字段清单项"""
    model: str          # 所属模型中文名
    field: str          # 字段中文名
    name: str           # 字段英文名
    algorithm: str      # 加密算法


class ResidueMeasureItem(Schema):
    """剩余信息保护措施项"""
    name: str
    detail: str
    owner: str          # 承担方（本平台 / 操作系统 …）


class TransportSecurityOut(Schema):
    """传输保密性现状"""
    enabled: bool
    protocol: str
    detail: str
    config_path: str


class TempUsageOut(Schema):
    """临时文件目录占用（剩余信息现状）"""
    file_count: int
    total_bytes: int
    total_mb: float


class ConfidentialityOverviewOut(Schema):
    """保密性保护总览（安全策略页「数据保密性」区块）"""
    encrypted_fields: List[EncryptedFieldItem]
    residue_measures: List[ResidueMeasureItem]
    transport: TransportSecurityOut
    temp_usage: TempUsageOut
    masked_log_keys: List[str]
