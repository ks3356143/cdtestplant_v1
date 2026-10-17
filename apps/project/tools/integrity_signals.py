"""
数据完整性标签自动刷新（GB/T 28452-2012 第三级 7.1.7）
apps.py ready() 中统一连接 post_save / post_delete 信号——覆盖一切写路径
（控制器、后台、脚本），无需逐接口埋点。
"""
from utils.audit import audit_log, EVENT_BUSINESS_CHANGE


def _watched(instance) -> bool:
    """该实例是否属于受保护模型"""
    from apps.project.tools.integrity import protected_models
    model_cls = type(instance)
    return any(e['model'] is model_cls for e in protected_models())


def refresh_on_save(sender, instance, **kwargs):
    """post_save：写操作提交后刷新/重建完整性标签"""
    try:
        if not _watched(instance):
            return
        from apps.project.tools.integrity import refresh_tag
        refresh_tag(instance)
    except Exception:
        pass  # 标签刷新绝不影响业务主流程


def audit_on_delete(sender, instance, **kwargs):
    """post_delete：受保护数据被删除 → 同步清理标签，并审计留痕（业务数据删除事件）"""
    try:
        if not _watched(instance):
            return
        from apps.system.models import DataIntegrityTag
        DataIntegrityTag.objects.filter(
            table_name=instance._meta.db_table, object_id=str(instance.pk)).delete()
        label = getattr(instance, 'ident', None) or getattr(instance, 'name', None) or instance.pk
        audit_log(None, EVENT_BUSINESS_CHANGE,
                  f'重要数据删除：{instance._meta.verbose_name} {label}；关联完整性标签已同步清理')
    except Exception:
        pass


def connect_signals():
    """只对受保护模型连接信号（avoid 全库开销）"""
    from apps.project.tools.integrity import protected_models
    from django.db.models.signals import post_delete, post_save

    for entry in protected_models():
        model = entry['model']
        post_save.connect(refresh_on_save, sender=model, dispatch_uid=f'integrity_save_{model.__name__}')
        post_delete.connect(audit_on_delete, sender=model, dispatch_uid=f'integrity_del_{model.__name__}')
