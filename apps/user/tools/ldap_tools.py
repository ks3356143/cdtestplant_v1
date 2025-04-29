import ldap
from django.contrib.auth import get_user_model

def load_ldap_users(url='ldap://dns.paisat.cn:389',
                    dn="CN=Administrator,CN=Users,DC=sstc,DC=ctu",
                    pwd="WXWX2019!!!!!!",
                    search_dn="OU=ALL,DC=sstc,DC=ctu",
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
        email_field = user[-1].get('mail', username_field + b'@sstc.ctu')[0]
        if isinstance(email_field, int):
            email_field = username_field + b'@sstc.ctu'
        user_dict = {
            'username': username_field.decode(),
            'name': user[-1]['name'][0].decode(),
            'email': email_field.decode(),
        }
        temp_users.append(user_dict)
        db_user = Users.objects.filter(username=user_dict['username'])
        exsits = db_user.exists()
        if exsits:
            # 如果存在则更新
            update_flag = False
            c_user = db_user.first()
            if c_user != user_dict['username']:
                c_user.username = user_dict['username']
                update_flag = True
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
            user_single.set_password('wxwx2018!!!')
            user_single.save()
            # 6月3日新增组别

