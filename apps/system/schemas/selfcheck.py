# -*- coding: utf-8 -*-
"""系统安全性检测分析（GB/T 28452-2012 第三级 7.1.10）相关 Schema"""
from datetime import datetime
from typing import List

from ninja import Schema


class CheckItemOut(Schema):
    """单个检测项"""
    category: str       # 被测对象：操作系统 / 数据库 / 网络 / 应用系统 / 硬件
    name: str           # 检测项名称
    method: str         # 检测方式
    status: str         # pass / risk / notice / na
    status_label: str   # 通过 / 风险 / 提示 / 不适用
    detail: str         # 检测结论说明
    advice: str = ''    # 整改建议


class CategoryStatOut(Schema):
    """按被测对象分组的统计"""
    name: str
    total: int
    risk: int
    na: int


class CheckSummaryOut(Schema):
    total: int
    passed: int
    risk: int
    notice: int
    na: int
    categories: List[CategoryStatOut]


class ImprovementOut(Schema):
    """依据检测结论已落地的改进（检测→改进闭环留痕）"""
    item: str
    finding: str
    action: str
    date: str


class SelfCheckOut(Schema):
    items: List[CheckItemOut]
    summary: CheckSummaryOut
    improvements: List[ImprovementOut]
    checked_at: datetime
