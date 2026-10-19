"""
项目级自主访问控制（GB/T 28452-2012 第三级 7.1.3 DAC）
- 客体（项目）负责人默认全权；负责人通过"项目成员"授权；移除成员即回收
- 仅系统管理员（admin）与负责人可管理成员（限制权限传播）
- 非授权用户访问项目数据一律 403（横向越权拦截）
匹配规则：duty_person / member 存的是用户显示名（name），同时兼容账号（username）
"""
import json as _json

from ninja_extra.exceptions import PermissionDenied

FORBIDDEN_MSG = '没有权限访问该项目数据（自主访问控制）'


def _user_identities(user) -> set:
    """用户的可匹配标识：显示名 + 账号"""
    if not getattr(user, 'is_authenticated', False):
        return set()
    identities = {getattr(user, 'name', None), getattr(user, 'username', None)}
    return {i for i in identities if i}


def _secret_level(value) -> int:
    """密级字典 key 转级别序号：1公开 < 2内部 < 3秘密★5年 < 4机密★10年 < 5绝密★20年"""
    try:
        return int(str(value).strip() or '1')
    except (ValueError, TypeError):
        return 1


def is_project_accessible(project, user) -> bool:
    """判断用户是否可访问项目：admin / 负责人 / 项目成员，且用户密级许可不低于项目密级（7.1.4 标记强制）"""
    if not getattr(user, 'is_authenticated', False):
        return False
    if getattr(user, 'role', None) == 'admin':
        return True
    identities = _user_identities(user)
    if not identities:
        return False
    is_member = getattr(project, 'duty_person', None) in identities
    if not is_member:
        member = getattr(project, 'member', None) or []
        if isinstance(member, str):
            try:
                member = _json.loads(member)
            except (ValueError, TypeError):
                member = []
        is_member = bool(identities & set(member or []))
    if not is_member:
        return False
    # 依据敏感标记执行访问控制：项目密级高于用户密级许可 → 拒绝
    if _secret_level(getattr(project, 'secret', '1')) > _secret_level(getattr(user, 'clearance', '1')):
        return False
    return True


def check_project_access(project, user):
    """校验项目访问权限，未授权抛 403（横向越权拦截）"""
    if not is_project_accessible(project, user):
        raise PermissionDenied(FORBIDDEN_MSG)


def check_project_access_by_id(project_id, user):
    """按项目 id 校验访问权限（fail-closed：拿不到明确的项目 id 一律拒绝）"""
    from apps.project.models import Project
    from django.shortcuts import get_object_or_404
    if project_id in (None, '', 0):
        raise PermissionDenied(FORBIDDEN_MSG)
    project = get_object_or_404(Project, id=project_id)
    check_project_access(project, user)
    return project


def accessible_project_ids(user) -> set:
    """当前用户可访问的项目 id 集合（用于列表过滤）"""
    from apps.project.models import Project
    return {p.id for p in Project.objects.all() if is_project_accessible(p, user)}


def ensure_creator_member(project, user):
    """项目创建后确保创建人可访问：非管理员创建时把创建人写进负责人/成员（授权起点）"""
    if not getattr(user, 'is_authenticated', False):
        return
    if getattr(user, 'role', None) == 'admin':
        return
    name = getattr(user, 'name', None) or getattr(user, 'username', '')
    username = getattr(user, 'username', '')
    if project.duty_person not in (name, username):
        member = project.member or []
        if name not in member and username not in member:
            member = member + [name]
    else:
        member = project.member or []
    project.member = member
    project.save(update_fields=['member'])


def is_project_manageable(project, user) -> bool:
    """项目管理权（改项目信息/删项目/管成员）：仅负责人与系统管理员——限制权限传播"""
    if not getattr(user, 'is_authenticated', False):
        return False
    if getattr(user, 'role', None) == 'admin':
        return True
    identities = _user_identities(user)
    return bool(identities) and getattr(project, 'duty_person', None) in identities


def check_project_manage(project, user):
    """非负责人/管理员修改或删除项目 → 403（防止成员自我提权）"""
    if not is_project_manageable(project, user):
        raise PermissionDenied('仅项目负责人或系统管理员可执行此操作（自主访问控制）')


def check_objects_access(model, ids, user, project_field='project'):
    """批量操作统一鉴权：逐个对象校验所属项目，任一不可访问即整体拒绝。

    同时校验 id 是否全部存在——避免"只校验第一行、其余行跨项目删除"的横向越权。
    返回对象列表（保持传入顺序）。
    """
    from django.shortcuts import get_object_or_404
    ids = list(ids or [])
    if not ids:
        from ninja.errors import HttpError
        raise HttpError(400, '请选择要操作的数据')
    objs = list(model.objects.filter(id__in=ids).select_related(project_field))
    found = {obj.id for obj in objs}
    missing = [i for i in ids if i not in found]
    if missing:
        from ninja.errors import HttpError
        raise HttpError(404, f'数据不存在或已被删除：{missing}')
    for obj in objs:
        check_project_access(getattr(obj, project_field), user)
    order = {obj_id: idx for idx, obj_id in enumerate(ids)}
    return sorted(objs, key=lambda o: order.get(o.id, 0))


def get_object_in_project(model, object_id, project_id, user):
    """按 id 取对象并校验：用户可访问该项目，且对象确实属于该项目。

    防止 update 类接口只校验 payload.project_id、却把别的项目的对象改掉/挪用。
    """
    project = check_project_access_by_id(project_id, user)
    from django.shortcuts import get_object_or_404
    obj = get_object_or_404(model, id=object_id)
    if getattr(obj, 'project_id', None) != project.id:
        raise PermissionDenied('数据不属于该测试项目，已拒绝操作（自主访问控制）')
    return obj
