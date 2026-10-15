"""
种入「用户角色」数据字典，供用户管理页下拉选择。
三权分立角色：admin 系统管理员 / secadmin 系统安全员 / auditadmin 系统审计员 / user 普通用户
"""
from django.db import migrations


def create_user_role_dict(apps, schema_editor):
    Dict = apps.get_model('dict', 'Dict')
    DictItem = apps.get_model('dict', 'DictItem')
    dict_obj, _ = Dict.objects.get_or_create(
        code='user_role',
        defaults={'name': '用户角色', 'status': '1', 'remark': '三权分立角色：系统管理员/系统安全员/系统审计员/普通用户'}
    )
    items = [
        ('admin', '系统管理员', 1),
        ('secadmin', '系统安全员', 2),
        ('auditadmin', '系统审计员', 3),
        ('user', '普通用户', 4),
    ]
    for key, title, sort in items:
        DictItem.objects.get_or_create(
            dict_id=dict_obj.id, key=key,
            defaults={'title': title, 'show_title': title, 'status': '1', 'sort': sort}
        )


def remove_user_role_dict(apps, schema_editor):
    Dict = apps.get_model('dict', 'Dict')
    DictItem = apps.get_model('dict', 'DictItem')
    DictItem.objects.filter(dict__code='user_role').delete()
    Dict.objects.filter(code='user_role').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0005_alter_users_role'),
        ('dict', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_user_role_dict, remove_user_role_dict),
    ]
