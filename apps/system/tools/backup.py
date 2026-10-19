# -*- coding: utf-8 -*-
"""
数据备份与故障恢复（GB/T 28452-2012 第三级 7.1.9）

对应国标两条子要求：
a) 用户自我信息备份与恢复 —— 用户可**有选择地**备份重要信息（选择项目范围），
   信息丢失/破坏后可按备份内容精准恢复；
b) 增量信息备份与恢复 —— 提供定时对**新增/变更**信息做增量备份的能力，
   恢复时按增量备份内容补齐。

实现方式：
- 备份内容 = 平台业务数据表（项目/轮次/被测件/设计需求/测试项/用例/用例步骤/
  问题单等）逐表导出为 JSON，落在 media/backup/ 下；
- 每条备份记录 SHA-256 摘要、条数、大小，便于事后核对完整性；
- 恢复按主键 upsert（存在则更新、不存在则新建），逐条 savepoint，
  单条失败不影响其余数据；恢复后回写 auto_now/auto_now_add 字段，保持原始时间。
- 抗抵赖证据（只增不改不删）与完整性标签（由业务数据自动重算）**不纳入备份恢复**。
"""
import hashlib
import json
import secrets
from datetime import datetime
from pathlib import Path

from django.core.serializers.json import DjangoJSONEncoder
from django.db import models, transaction
from django.db.models import Q

# 纳入备份的业务模型（顺序即恢复的优先顺序基准，实际按外键依赖自动排序）
from apps.dict.models import Dict
from apps.project.models import (Abbreviation, Case, CaseStep, Contact, Design, Dut, DutMetrics,
                                 DynamicHardwareTable, DynamicSoftTable, EnvAnalysis, EvaluateData,
                                 InfluenceArea, InfluenceItem, JKDesignInfo, Problem,
                                 Project, ProjectDynamicDescription, ProjectSoftSummary, Round,
                                 StaticSoftHardware, StaticSoftItem, StuctSortData, TestDemand,
                                 TestDemandContent, TestDemandContentStep)

BACKUP_MODELS = [
    Project, Round, Dut, DutMetrics, Design, JKDesignInfo,
    TestDemand, TestDemandContent, TestDemandContentStep,
    Case, CaseStep, Problem,
    ProjectSoftSummary, ProjectDynamicDescription, StaticSoftItem, StaticSoftHardware,
    DynamicSoftTable, DynamicHardwareTable, EvaluateData, EnvAnalysis,
    StuctSortData, InfluenceArea, InfluenceItem,
    Contact, Abbreviation, Dict,
]

# 数据结构版本，便于将来兼容旧备份文件
BACKUP_FORMAT = 'cdtestplant-backup-v1'


def backup_dir() -> Path:
    """备份文件目录（随 media 一起存放，不进版本库）"""
    from django.conf import settings
    path = Path(settings.BASE_DIR) / 'media' / 'backup'
    path.mkdir(parents=True, exist_ok=True)
    return path


def _label(model) -> str:
    """模型的稳定标识：app_label.ModelName（跨版本不随中文名变化）"""
    return f'{model._meta.app_label}.{model.__name__}'


def _has_field(model, name: str) -> bool:
    return any(f.name == name for f in model._meta.fields)


def _auto_fields(model) -> set:
    """auto_now / auto_now_add 字段：正常 save 会被覆盖，恢复后需回写原值"""
    return {f.name for f in model._meta.fields
            if getattr(f, 'auto_now', False) or getattr(f, 'auto_now_add', False)}


def _changed_since_condition(model, since: datetime):
    """
    增量筛选条件：优先按最后修改时间（update_datetime），退化为创建时间。
    两者都没有的模型（纯关系子表）无法判定增量，整表带上（宁可多备不可漏备）。
    """
    for name in ('update_datetime', 'create_datetime'):
        field = next((f for f in model._meta.fields if f.name == name), None)
        if field is None:
            continue
        # CoreModel 的时间字段是 DateField，比较值也要降到"天"粒度
        value = since if isinstance(field, models.DateTimeField) else since.date()
        return Q(**{f'{name}__gte': value})
    return None


def collect_rows(project_id=None, since=None) -> dict:
    """
    采集待备份数据。
    :param project_id: 指定项目时只备份该项目及其下游数据；None 表示全部业务数据
    :param since: 增量水位线（只取该时间之后新增/变更的数据）；None 表示全量
    :return: {模型标识: [行字典, ...]}
    """
    result = {}
    ids = {}

    # 第一轮：项目本体 + 直接挂项目的表
    for model in BACKUP_MODELS:
        qs = model.objects.all()
        if project_id is not None:
            if model is Project:
                qs = qs.filter(id=project_id)
            elif _has_field(model, 'project'):
                qs = qs.filter(project_id=project_id)
            else:
                continue          # 与项目无直接关联的子表，交给下面的父子推导
        if since is not None:
            cond = _changed_since_condition(model, since)
            if cond is not None:
                qs = qs.filter(cond)
        rows = list(qs.values())
        result[_label(model)] = rows
        ids[model] = {r[model._meta.pk.attname] for r in rows}

    # 后续轮次：按外键把子表数据带进来（如 用例 -> 用例步骤、测试项 -> 测试项内容）
    for _ in range(6):
        changed = False
        for model in BACKUP_MODELS:
            if _label(model) in result:
                continue
            cond = None
            for field in model._meta.get_fields():
                if not (field.is_relation and field.many_to_one):
                    continue
                parent = field.related_model
                parent_ids = ids.get(parent)
                if not parent_ids:
                    continue
                item = Q(**{f'{field.name}__in': list(parent_ids)})
                cond = item if cond is None else (cond | item)
            if cond is None:
                continue
            rows = list(model.objects.filter(cond).values())
            result[_label(model)] = rows
            ids[model] = {r[model._meta.pk.attname] for r in rows}
            changed = True
        if not changed:
            break

    return result


def _restore_order(models):
    """按外键依赖排序（父表在前），有环时剩余模型追加在末尾兜底"""
    order, placed, remaining = [], set(), list(models)
    for _ in range(len(models) + 2):
        for model in list(remaining):
            deps = {f.related_model for f in model._meta.get_fields()
                    if f.is_relation and f.many_to_one
                    and f.related_model in models and f.related_model is not model}
            if deps <= placed:
                order.append(model)
                placed.add(model)
                remaining.remove(model)
        if not remaining:
            break
    order.extend(remaining)
    return order


def _label_map():
    return {_label(m): m for m in BACKUP_MODELS}


def create_backup(kind: str, project_id, name: str, creator) -> tuple:
    """
    执行一次性备份。
    :return: (BackupRecord, 采集到的表统计 dict)
    """
    from apps.system.models import BackupRecord
    since = None
    if kind == 'incremental':
        # 增量水位线：同范围内的最近一次成功备份时间；没有历史备份则退化为全量
        last = BackupRecord.objects.filter(kind__in=('full', 'incremental'), status='success')
        if project_id is not None:
            last = last.filter(scope_project_id=project_id)
        last = last.order_by('-create_datetime').first()
        if last:
            since = last.create_datetime

    data = collect_rows(project_id=project_id, since=since)
    total = sum(len(rows) for rows in data.values())
    payload = {
        'format': BACKUP_FORMAT,
        'kind': kind,
        'scope_project_id': project_id,
        'since': since.isoformat() if since else None,
        'created_at': datetime.now().isoformat(),
        'app_version': 'v0.1.2',
        'data': data,
    }
    stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    # 加随机后缀：同一秒内连续做多次备份（不同范围）时文件名不能相互覆盖
    file_name = f'backup_{stamp}_{kind}_{secrets.token_hex(3)}.json'
    path = backup_dir() / file_name
    blob = json.dumps(payload, cls=DjangoJSONEncoder, ensure_ascii=False, sort_keys=True)
    path.write_text(blob, encoding='utf-8')

    digest = hashlib.sha256(blob.encode('utf-8')).hexdigest()
    size = path.stat().st_size

    scope_label = '全部业务数据'
    if project_id is not None:
        project = Project.objects.filter(id=project_id).first()
        scope_label = f'项目 {project.ident if project else project_id} - {project.name if project else ""}'.strip()

    record = BackupRecord.objects.create(
        name=name or f'{stamp} {("全量" if kind == "full" else "增量")}备份',
        kind=kind, scope_label=scope_label, scope_project_id=project_id,
        file_name=file_name, size_bytes=size, record_count=total, digest=digest,
        status='success', creator=creator,
        message=f'覆盖 {len(data)} 张业务表',
    )
    return record, {k: len(v) for k, v in data.items() if v}


def verify_backup(record) -> bool:
    """核对备份文件未被改动：重算 SHA-256 与记录比对"""
    path = backup_dir() / record.file_name
    if not path.is_file():
        return False
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return digest == record.digest


def restore_backup(record) -> dict:
    """
    按备份内容恢复数据：按主键 upsert，逐条 savepoint，单条失败不影响其余。
    :return: {'created', 'updated', 'failed', 'models': {...}}
    """
    path = backup_dir() / record.file_name
    if not path.is_file():
        raise FileNotFoundError(f'备份文件不存在：{record.file_name}')
    payload = json.loads(path.read_text(encoding='utf-8'))
    data = payload.get('data') or {}

    label_map = _label_map()
    models = [label_map[label] for label in data if label in label_map]
    stats = {'created': 0, 'updated': 0, 'failed': 0, 'models': {}}

    for model in _restore_order(models):
        rows = data.get(_label(model)) or []
        if not rows:
            continue
        created = updated = failed = 0
        autos = _auto_fields(model)
        pk_name = model._meta.pk.attname      # 部分表以 project/round 作主键，主键列名不都是 id
        for row in rows:
            pk = row.get(pk_name)
            defaults = {k: v for k, v in row.items() if k != pk_name}
            try:
                with transaction.atomic():          # 每条一个 savepoint
                    if pk is None:
                        model.objects.create(**defaults)
                        created += 1
                        continue
                    obj, is_new = model.objects.update_or_create(
                        **{pk_name: pk}, defaults=defaults)
                    # auto_now / auto_now_add 字段会被 Django 覆盖，这里按备份原值回写
                    restore_auto = {k: row[k] for k in autos if k in row}
                    if restore_auto:
                        model.objects.filter(pk=obj.pk).update(**restore_auto)
                    created += 1 if is_new else 0
                    updated += 0 if is_new else 1
            except Exception:
                failed += 1
        stats['created'] += created
        stats['updated'] += updated
        stats['failed'] += failed
        stats['models'][str(model._meta.verbose_name)] = {
            'created': created, 'updated': updated, 'failed': failed,
        }
    return stats


def delete_backup(record) -> bool:
    """删除备份记录及其文件"""
    path = backup_dir() / record.file_name
    removed = False
    if path.is_file():
        try:
            path.unlink()
            removed = True
        except OSError:
            removed = False
    record.delete()
    return removed


def backup_summary() -> dict:
    """备份现状概览（供页面展示）"""
    from apps.system.models import BackupRecord
    qs = BackupRecord.objects.all()
    total = qs.count()
    latest = qs.order_by('-create_datetime').first()
    return {
        'total': total,
        'full': qs.filter(kind='full').count(),
        'incremental': qs.filter(kind='incremental').count(),
        'total_records': sum(qs.values_list('record_count', flat=True)) if total else 0,
        'latest_time': latest.create_datetime if latest else None,
        'model_count': len(BACKUP_MODELS),
    }
