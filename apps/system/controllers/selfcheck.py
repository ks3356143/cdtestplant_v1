# -*- coding: utf-8 -*-
"""
系统安全性检测分析接口（GB/T 28452-2012 第三级 7.1.10）

系统安全员在「安全策略 - 安全性检测分析」页一键执行自检：
按操作系统 / 数据库 / 网络 / 应用系统 / 硬件五类被测对象逐项给出结论与整改建议，
并列出依据检测结论已落地的改进，形成"检测分析 → 整改"闭环记录。
"""
from datetime import datetime

from ninja_extra import api_controller, ControllerBase, route
from ninja_extra.permissions import IsAuthenticated
from ninja_jwt.authentication import JWTAuth

from apps.system.schemas.selfcheck import SelfCheckOut
from apps.system.tools.security_check import run_security_check
from utils.audit import EVENT_SECURITY_SCAN, audit_log
from utils.permissions import IsSecurityAdmin


@api_controller("/system/security", auth=JWTAuth(), permissions=[IsAuthenticated, IsSecurityAdmin],
                tags=['系统安全性检测分析'])
class SecuritySelfCheckController(ControllerBase):
    """7.1.10：应用软件系统安全性检测分析（自检）"""

    @route.get("/selfcheck", response=SelfCheckOut, url_name="security-selfcheck")
    def selfcheck(self):
        result = run_security_check()
        summary = result['summary']
        # 自检动作本身留痕（7.1.6 审计），便于事后追溯谁在何时做过检测
        audit_log(self.context.request, EVENT_SECURITY_SCAN,
                  f'安全性检测分析：执行全项自检，共 {summary["total"]} 项 —— '
                  f'通过 {summary["passed"]}、风险 {summary["risk"]}、'
                  f'提示 {summary["notice"]}、不适用 {summary["na"]}')
        result['checked_at'] = datetime.now()
        return result
