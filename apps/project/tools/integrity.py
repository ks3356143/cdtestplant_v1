"""
重要敏感数据完整性标签（GB/T 28452-2012 第三级 7.1.7）
- DataIntegrityTag：对受保护数据的关键字段快照计算 SHA256，作为"完整性校验标签"
- 时机：业务写操作事务提交后刷新标签（protect_model 信号后置）；审计员可批量核查
- 判定：当前数据重算摘要 ≠ 标签 → 数据完整性破损（多为绕过应用直改数据库）
- 恢复：平台负责检测与告警；修复依赖数据库备份导入（dbdata.sql 导出机制），如实标注
"""
import hashlib
import json

# 受保护的重要敏感数据登记表：模型 → 参与摘要的关键字段（排序后参与计算）
PROTECTED_MODELS = []


def register(model, fields):
    PROTECTED_MODELS.append({'model': model, 'fields': list(fields)})


_PROTECTED_CACHE = None


def protected_models():
    """懒加载登记表（避免 app 加载期 import 循环）"""
    global _PROTECTED_CACHE
    if _PROTECTED_CACHE is None:
        from apps.project.models import Project, Case, CaseStep, Problem
        register(Project, ['ident', 'name', 'beginTime', 'endTime', 'duty_person', 'member',
                           'secret', 'security_level', 'test_level', 'report_type', 'step',
                           'quality_person', 'vise_person', 'config_person', 'soft_type'])
        register(Case, ['ident', 'name', 'initialization', 'premise', 'summarize',
                        'designPerson', 'testPerson', 'monitorPerson', 'exe_time'])
        register(CaseStep, ['expect', 'passed'])  # 用例步骤执行结果：关键业务判定数据
        register(Problem, ['ident', 'name', 'status', 'grade', 'type', 'closeMethod',
                           'postPerson', 'postDate', 'operation'])
        _PROTECTED_CACHE = PROTECTED_MODELS
    return _PROTECTED_CACHE


def _normalize(value):
    """参与摘要的值标准化：日期等对象转 str；None→''"""
    if value is None:
        return ''
    return str(value)


def compute_digest(instance, fields) -> str:
    """对关键字段快照（排序 JSON）计算 SHA256 摘要"""
    snapshot = {f: _normalize(getattr(instance, f, None)) for f in sorted(fields)}
    payload = json.dumps(snapshot, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()


def refresh_tag(instance) -> 'object':
    """写操作后刷新（或首次创建）数据完整标签；返回标签对象"""
    from apps.system.models import DataIntegrityTag
    if not getattr(instance, 'pk', None):
        return None
    table = instance._meta.db_table
    for entry in protected_models():
        if entry['model'] is type(instance):
            digest = compute_digest(instance, entry['fields'])
            tag, _ = DataIntegrityTag.objects.update_or_create(
                table_name=table, object_id=str(instance.pk),
                defaults={'digest': digest, 'algorithm': 'SHA256'})
            return tag
    return None


def refresh_tags(instances) -> int:
    """批量刷新同一模型的完整性标签（供 bulk_update 等不触发 post_save 的写路径使用）

    一次查询已有标签 + 批量写入，避免逐条 update_or_create 的 N+1。
    """
    from apps.system.models import DataIntegrityTag
    from django.utils import timezone
    instances = [i for i in instances if getattr(i, 'pk', None)]
    if not instances:
        return 0
    model_cls = type(instances[0])
    entry = next((e for e in protected_models() if e['model'] is model_cls), None)
    if entry is None:
        return 0
    table = model_cls._meta.db_table
    digests = {str(i.pk): compute_digest(i, entry['fields']) for i in instances}
    existing = {t.object_id: t
                for t in DataIntegrityTag.objects.filter(table_name=table, object_id__in=digests)}
    now = timezone.now()
    to_create, to_update = [], []
    for object_id, digest in digests.items():
        tag = existing.get(object_id)
        if tag is None:
            to_create.append(DataIntegrityTag(table_name=table, object_id=object_id, digest=digest,
                                              algorithm='SHA256', update_datetime=now, create_datetime=now))
        elif tag.digest != digest or tag.algorithm != 'SHA256':
            tag.digest = digest
            tag.algorithm = 'SHA256'
            tag.update_datetime = now
            to_update.append(tag)
    if to_create:
        DataIntegrityTag.objects.bulk_create(to_create)
    if to_update:
        DataIntegrityTag.objects.bulk_update(to_update, ['digest', 'algorithm', 'update_datetime'])
    return len(to_create) + len(to_update)


def verify_all():
    """批量核查全部受保护数据：返回 [{object, fields, expected, actual, intact, broken}]"""
    from apps.system.models import DataIntegrityTag
    results = []
    tags = {(t.table_name, t.object_id): t for t in DataIntegrityTag.objects.all()}
    for entry in protected_models():
        model, fields = entry['model'], entry['fields']
        table = model._meta.db_table
        for instance in model.objects.all():
            key = (table, str(instance.pk))
            tag = tags.get(key)
            if tag is None:
                # 未建标签的数据先补建（视为完好，下一次有基准）
                refresh_tag(instance)
                continue
            actual = compute_digest(instance, fields)
            intact = actual == tag.digest
            results.append({
                'table': table,
                'id': instance.pk,
                'label': f'{instance._meta.verbose_name} #{instance.pk}',
                'ident': getattr(instance, 'ident', None) or getattr(instance, 'name', None) or '',
                'algorithm': tag.algorithm,
                'stored': tag.digest[:16],
                'actual': actual[:16],
                'intact': intact,
                'checked_at': tag.update_datetime,
            })
    return results
