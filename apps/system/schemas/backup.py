# -*- coding: utf-8 -*-
"""数据备份与恢复（GB/T 28452-2012 第三级 7.1.9）相关 Schema"""
from datetime import datetime
from typing import Literal

from ninja import Schema
from pydantic import Field


class BackupCreateSchema(Schema):
    """新建备份入参"""
    name: str = Field('', max_length=200, description='备份名称，留空自动生成')
    kind: Literal['full', 'incremental'] = Field('full', description='full 全量 / incremental 增量')
    project_id: int | None = Field(None, description='指定项目 id；不传表示全部业务数据（需系统管理员）')


class BackupRecordOutSchema(Schema):
    """备份记录展示项"""
    id: int
    name: str
    kind: str
    kind_label: str
    scope_label: str
    scope_project_id: int | None = None
    file_name: str
    size_bytes: int
    size_text: str
    record_count: int
    digest: str
    status: str
    message: str | None = None
    creator_name: str | None = None
    create_datetime: datetime
    file_exists: bool


class BackupSummaryOutSchema(Schema):
    """备份现状概览"""
    total: int
    full: int
    incremental: int
    total_records: int
    latest_time: datetime | None = None
    model_count: int
