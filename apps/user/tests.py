# -*- coding: utf-8 -*-
"""
apps/user 单元测试 —— 字段级加密与盲索引（GB/T 28452-2012 第三级 7.1.8）

运行：python manage.py test apps.user
"""
from django.db import connection
from django.test import TestCase

from apps.user.models import Users
from utils.crypto import (ENCRYPTED_PREFIX, blind_index, decrypt_value, encrypt_value,
                          is_encrypted)


class CryptoUnitTests(TestCase):
    """加解密工具本身的行为"""

    def test_roundtrip(self):
        for plain in ('13800001111', 'srs@example.com', '含中文的取值'):
            token = encrypt_value(plain)
            self.assertTrue(is_encrypted(token))
            self.assertNotIn(plain, token)          # 密文里不应出现明文
            self.assertEqual(decrypt_value(token), plain)

    def test_encrypt_is_idempotent(self):
        """已加密的值不会二次加密（数据迁移与重复保存都依赖这一点）"""
        token = encrypt_value('13800001111')
        self.assertEqual(encrypt_value(token), token)

    def test_empty_values_pass_through(self):
        for value in (None, '', 0):
            self.assertEqual(encrypt_value(value), value)
            self.assertEqual(decrypt_value(value), value)

    def test_same_plaintext_differs(self):
        """Fernet 带随机 IV：同一明文两次加密的密文不同"""
        self.assertNotEqual(encrypt_value('13800001111'), encrypt_value('13800001111'))

    def test_decrypt_garbage_does_not_raise(self):
        """密文被破坏时返回占位串而不是抛异常，避免拖垮列表接口"""
        self.assertEqual(decrypt_value(ENCRYPTED_PREFIX + 'not-a-token'), '<解密失败>')

    def test_blind_index(self):
        self.assertEqual(blind_index('13800001111'), blind_index(' 13800001111 '))
        self.assertNotEqual(blind_index('13800001111'), blind_index('13800001112'))
        self.assertEqual(blind_index(''), '')
        self.assertEqual(blind_index(None), '')
        self.assertEqual(len(blind_index('x')), 64)


class UsersEncryptedFieldTests(TestCase):
    """用户表敏感字段：落库为密文、读出来是明文、盲索引自动维护"""

    def setUp(self):
        self.user = Users.objects.create_user(
            username='unit_test_user', password='UnitTest#2026', name='单测用户',
            phone='13912345678', email='unit@example.com')

    def tearDown(self):
        Users.objects.filter(username='unit_test_user').delete()

    def _raw(self, column):
        """绕开 ORM 直接读库，确认落库形态"""
        with connection.cursor() as cur:
            cur.execute(f'SELECT {column} FROM user_user WHERE username=%s', ['unit_test_user'])
            return cur.fetchone()[0]

    def test_phone_and_email_stored_encrypted(self):
        self.assertTrue(self._raw('phone').startswith(ENCRYPTED_PREFIX))
        self.assertTrue(self._raw('email').startswith(ENCRYPTED_PREFIX))
        self.assertNotIn('13912345678', self._raw('phone'))

    def test_model_reads_plaintext(self):
        fresh = Users.objects.get(username='unit_test_user')
        self.assertEqual(fresh.phone, '13912345678')
        self.assertEqual(fresh.email, 'unit@example.com')

    def test_phone_index_maintained(self):
        self.assertEqual(self._raw('phone_index'), blind_index('13912345678'))
        # 改电话后索引随之更新
        self.user.phone = '13700007777'
        self.user.save()
        self.assertEqual(self._raw('phone_index'), blind_index('13700007777'))

    def test_queryset_update_also_encrypts(self):
        """update() 走 get_prep_value，同样落密文（批量维护路径不能漏）"""
        Users.objects.filter(username='unit_test_user').update(phone='13600006666')
        raw = self._raw('phone')
        self.assertTrue(raw.startswith(ENCRYPTED_PREFIX))
        self.assertEqual(Users.objects.get(username='unit_test_user').phone, '13600006666')

    def test_search_by_phone_index(self):
        """加密列不能 LIKE，按电话检索走盲索引等值匹配"""
        found = Users.objects.filter(phone_index=blind_index('13912345678'))
        self.assertEqual([u.username for u in found], ['unit_test_user'])
        self.assertFalse(Users.objects.filter(phone_index=blind_index('19900000000')).exists())
