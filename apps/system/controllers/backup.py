# -*- coding: utf-8 -*-
"""
数据备份与故障恢复接口（GB/T 28452-2012 第三级 7.1.9）

- 用户自我信息备份与恢复（a）：登录用户可**按项目**选择范围做备份，
  之后按该备份精准恢复；全量备份（影响面大）限系统管理员。
- 增量信息备份与恢复（b）：支持「增量备份」，只带走上次备份之后新增/变更的数据，
  也可由计划任务定时调用 manage.py 命令触发（见 apps/system/tools/backup.py）。
- 每条备份记录 SHA-256 摘要，页面可核对文件未被改动；恢复为按主键 upsert，可重复执行。
"""

from django.http import FileResponse
from django.shortcuts import get_object_or_404
from ninja_extra import api_controller, ControllerBase, route
from ninja_extra.permissions import IsAuthenticated
from ninja_jwt.authentication import JWTAuth

from apps.project.tools.access_control import check_project_access_by_id
from apps.system.models import BackupRecord
from apps.system.schemas.backup import BackupCreateSchema, BackupRecordOutSchema, BackupSummaryOutSchema
from apps.system.tools.backup import (backup_dir, backup_summary, create_backup, delete_backup,
                                      restore_backup, verify_backup)
from utils.audit import audit_log, EVENT_BUSINESS_CHANGE
from utils.chen_response import ChenResponse


def _size_text(size: int) -> str:
    if size >= 1024 * 1024:
        return f'{size / 1024 / 1024:.2f} MB'
    if size >= 1024:
        return f'{size / 1024:.1f} KB'
    return f'{size} B'


def _to_out(record) -> dict:
    creator = record.creator
    return {
        'id': record.id,
        'name': record.name,
        'kind': record.kind,
        'kind_label': record.get_kind_display(),
        'scope_label': record.scope_label,
        'scope_project_id': record.scope_project_id,
        'file_name': record.file_name,
        'size_bytes': record.size_bytes,
        'size_text': _size_text(record.size_bytes),
        'record_count': record.record_count,
        'digest': record.digest,
        'status': record.status,
        'message': record.message,
        'creator_name': getattr(creator, 'name', None) or getattr(creator, 'username', None),
        'create_datetime': record.create_datetime,
        'file_exists': (backup_dir() / record.file_name).is_file(),
    }


@api_controller("/system/backup", auth=JWTAuth(), permissions=[IsAuthenticated],
                tags=['数据备份与恢复'])
class BackupController(ControllerBase):
    """7.1.9：用户自我信息备份/恢复 + 定时增量备份"""

    # ------------------------------ 查询 ------------------------------

    @route.get("/summary", response=BackupSummaryOutSchema, url_name="backup-summary")
    def summary(self):
        return backup_summary()

    @route.get("/list", response=list[BackupRecordOutSchema], url_name="backup-list")
    def list_backup(self):
        user = self.context.request.user
        qs = BackupRecord.objects.select_related('creator').all()
        # 列表只返回有权查看的备份：项目备份按项目访问权限过滤；全量备份仅管理员或创建者本人
        if getattr(user, 'role', None) != 'admin':
            from django.db.models import Q
            from apps.project.tools.access_control import accessible_project_ids
            allowed = accessible_project_ids(user)
            qs = qs.filter(Q(scope_project_id__in=allowed) |
                           Q(scope_project_id__isnull=True, creator_id=getattr(user, 'id', None)))
        return [_to_out(r) for r in qs]

    # ------------------------------ 备份 ------------------------------

    @route.post("/create", url_name="backup-create")
    def create(self, payload: BackupCreateSchema):
        user = self.context.request.user
        if payload.project_id is None:
            # 全量备份影响面大（含全部项目数据），限系统管理员
            if getattr(user, 'role', None) != 'admin':
                return ChenResponse(code=403, status=403,
                                    message='全量备份涉及全部项目数据，仅系统管理员可执行；请选择具体项目范围')
        else:
            check_project_access_by_id(payload.project_id, user)   # 越权抛 403

        record, table_stats = create_backup(payload.kind, payload.project_id, payload.name, user)
        audit_log(self.context.request, EVENT_BUSINESS_CHANGE,
                  f'数据备份：{record.name}（{record.get_kind_display()}，范围 {record.scope_label}），'
                  f'共 {record.record_count} 条数据，SHA-256 摘要 {record.digest[:16]}…')
        return ChenResponse(data=_to_out(record),
                            message=f'备份完成：{record.record_count} 条数据，{_size_text(record.size_bytes)}')

    # ------------------------------ 恢复 ------------------------------

    @route.post("/{record_id}/restore", url_name="backup-restore")
    def restore(self, record_id: int):
        user = self.context.request.user
        record = get_object_or_404(BackupRecord, id=record_id)
        if not verify_backup(record):
            return ChenResponse(code=400, status=400,
                                message='备份文件缺失或摘要不一致，已拒绝恢复（防止用被篡改的备份覆盖数据）')
        # 恢复数据的授权：备份创建者本人，或系统管理员
        if record.scope_project_id is not None:
            check_project_access_by_id(record.scope_project_id, user)
        elif getattr(user, 'role', None) != 'admin' and record.creator_id != getattr(user, 'id', None):
            return ChenResponse(code=403, status=403, message='全量备份的恢复仅限系统管理员或备份创建者本人')

        stats = restore_backup(record)
        audit_log(self.context.request, EVENT_BUSINESS_CHANGE,
                  f'数据恢复：按备份「{record.name}」恢复，新增 {stats["created"]} 条、'
                  f'更新 {stats["updated"]} 条、失败 {stats["failed"]} 条')
        detail = '；'.join(f'{name} +{v["created"]}/~{v["updated"]}'
                           for name, v in list(stats['models'].items())[:6])
        return ChenResponse(data=stats,
                            message=f'恢复完成：新增 {stats["created"]} 条，更新 {stats["updated"]} 条'
                                    + (f'，失败 {stats["failed"]} 条' if stats['failed'] else '')
                                    + (f'（{detail}）' if detail else ''))

    # ------------------------------ 下载 / 删除 ------------------------------

    @route.get("/{record_id}/download", url_name="backup-download")
    def download(self, record_id: int):
        user = self.context.request.user
        record = get_object_or_404(BackupRecord, id=record_id)
        # 与恢复同一授权口径：项目备份校验项目访问权；全量备份仅管理员或创建者
        if record.scope_project_id is not None:
            check_project_access_by_id(record.scope_project_id, user)
        elif getattr(user, 'role', None) != 'admin' and record.creator_id != getattr(user, 'id', None):
            return ChenResponse(code=403, status=403, message='全量备份的下载仅限系统管理员或备份创建者本人')
        path = backup_dir() / record.file_name
        if not path.is_file():
            return ChenResponse(code=404, status=404, message='备份文件已不存在')
        return FileResponse(open(path, 'rb'),
                            content_type='application/json',
                            filename=record.file_name)

    @route.delete("/{record_id}", url_name="backup-delete")
    def delete(self, record_id: int):
        user = self.context.request.user
        record = get_object_or_404(BackupRecord, id=record_id)
        if getattr(user, 'role', None) != 'admin' and record.creator_id != getattr(user, 'id', None):
            return ChenResponse(code=403, status=403, message='只能删除自己创建的备份')
        name = record.name
        delete_backup(record)
        audit_log(self.context.request, EVENT_BUSINESS_CHANGE, f'数据备份删除：{name}')
        return ChenResponse(code=200, status=200, message='删除成功')
