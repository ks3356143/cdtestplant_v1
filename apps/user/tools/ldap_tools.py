import secrets

import ldap
from django.conf import settings
from django.contrib.auth import get_user_model

# 1. 连接参数统一由 settings/.env 提供，避免在此重复硬编码凭据
server_uri = settings.AUTH_LDAP_SERVER_URI
dn = settings.AUTH_LDAP_BIND_DN
password = settings.AUTH_LDAP_BIND_PASSWORD
base_dn = getattr(settings, 'BASE_DN', 'OU=all,DC=sstc,DC=ctu')

# 3. 连接LDAP服务器进行操作
def load_ldap_users(url=server_uri,
                    dn=dn,
                    pwd=password,
                    search_dn=base_dn,
                    search_filter='(&(sAMAccountName=*))'):
    Users = get_user_model()

    ldap_server = ldap.initialize(url)
    ldap_server.simple_bind_s(dn, pwd)
    ldap_users = ldap_server.search_ext_s(search_dn,
                                          ldap.SCOPE_SUBTREE,
                                          search_filter)

    temp_users = []
    for user in ldap_users:
        username_field = user[-1]['sAMAccountName'][0]
        # mail 为 LDAP 属性列表（值可能是 bytes）；取列表首项，缺失/为空时回退到默认邮箱
        # （原实现写成 .get('mail', 默认)[0]：mail 缺失时默认值是 bytes，[0] 返回 int，
        #  再靠 isinstance(int) 分支兜底，逻辑晦涩；此处直接按真实类型处理）
        mail_values = user[-1].get('mail')
        email_field = mail_values[0] if mail_values else username_field + b'@sstc.ctu'
        user_dict = {
            'username': username_field.decode(),
            'name': user[-1]['name'][0].decode(),
            'email': email_field.decode(),
        }
        temp_users.append(user_dict)
        db_user = Users.objects.filter(username=user_dict['username'])
        exsits = db_user.exists()
        if exsits:
            # 如果存在则更新资料；绝不能重置本地口令（LDAP 用户走 LDAP 认证，重置会覆盖本地密码）
            update_flag = False
            c_user = db_user.first()
            if c_user.name != user_dict['name']:
                c_user.name = user_dict['name']
                update_flag = True
            if c_user.email != user_dict['email']:
                c_user.email = user_dict['email']
                update_flag = True
            if update_flag:
                c_user.save()
        else:
            user_dict['remark'] = '自动同步LDAP数据用户'
            user_dict['status'] = '1'
            user_dict['phone'] = '18888888888'
            user_dict['role'] = 'user'
            user_dict['accountId'] = 'user'
            user_single = Users.objects.create(**user_dict)
            # 随机初始口令：LDAP 用户通过 LDAP 认证，本地口令不对外使用
            user_single.set_password(secrets.token_urlsafe(24))
            user_single.save()
            # 6月3日新增组别

