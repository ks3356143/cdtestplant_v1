# -*- coding: utf-8 -*-
"""
把 users 表里既有的明文电话/邮箱就地加密，并回填电话盲索引（GB/T 28452-2012 7.1.8）。

- 正向：明文（历史数据）→ 密文；已是密文的值不会二次加密（encrypt_value 幂等）
- 反向：密文 → 明文，便于回滚；解不开的密文按原样保留，不会丢数据
"""
from django.db import migrations

from utils.crypto import blind_index, decrypt_value, encrypt_value


def encrypt_existing(apps, schema_editor):
    Users = apps.get_model('user', 'Users')
    # 逐条处理：user_user 表量级很小（百级），不必为省几次查询引入批量 SQL 拼接
    for user in Users.objects.all().iterator():
        # 历史模型没有自定义 save()，盲索引需要显式回填
        Users.objects.filter(pk=user.pk).update(
            phone=encrypt_value(user.phone),
            email=encrypt_value(user.email),
            phone_index=blind_index(user.phone),
        )


def decrypt_existing(apps, schema_editor):
    Users = apps.get_model('user', 'Users')
    for user in Users.objects.all().iterator():
        Users.objects.filter(pk=user.pk).update(
            phone=decrypt_value(user.phone),
            email=decrypt_value(user.email),
            phone_index='',
        )


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0008_users_phone_index_alter_users_email_and_more'),
    ]

    operations = [
        migrations.RunPython(encrypt_existing, decrypt_existing),
    ]
