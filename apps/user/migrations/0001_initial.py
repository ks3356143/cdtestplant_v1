# Generated by Django 4.2.13 on 2024-07-03 10:30

from django.conf import settings
import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Users',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('id', models.BigAutoField(help_text='Id', primary_key=True, serialize=False, verbose_name='Id')),
                ('remark', models.CharField(blank=True, help_text='描述', max_length=255, null=True, verbose_name='描述')),
                ('update_datetime', models.DateField(auto_now=True, help_text='修改时间', null=True, verbose_name='修改时间')),
                ('create_datetime', models.DateField(auto_now_add=True, help_text='创建时间', null=True, verbose_name='创建时间')),
                ('sort', models.IntegerField(blank=True, default=1, help_text='显示排序', null=True, verbose_name='显示排序')),
                ('username', models.CharField(db_index=True, help_text='用户账号', max_length=150, unique=True, verbose_name='用户账号')),
                ('name', models.CharField(help_text='姓名', max_length=40, verbose_name='姓名')),
                ('avatar', models.TextField(blank=True, help_text='头像', null=True, verbose_name='头像')),
                ('email', models.EmailField(blank=True, help_text='邮箱', max_length=255, null=True, verbose_name='邮箱')),
                ('status', models.CharField(default='1', help_text='status', max_length=15, verbose_name='启用状态')),
                ('job', models.CharField(blank=True, help_text='工作', max_length=255, null=True, verbose_name='工作')),
                ('jobName', models.CharField(blank=True, help_text='工作名称', max_length=255, null=True, verbose_name='工作名称')),
                ('organization', models.CharField(blank=True, help_text='工作组织', max_length=255, null=True, verbose_name='工作组织')),
                ('location', models.CharField(blank=True, help_text='住地', max_length=255, null=True, verbose_name='住地')),
                ('locationName', models.CharField(blank=True, help_text='住地名称', max_length=255, null=True, verbose_name='住地名称')),
                ('introduction', models.CharField(blank=True, help_text='自我介绍', max_length=255, null=True, verbose_name='自我介绍')),
                ('personalWebsite', models.CharField(blank=True, help_text='个人网站', max_length=255, null=True, verbose_name='个人网站')),
                ('phone', models.CharField(blank=True, default='18888888888', help_text='电话', max_length=255, null=True, verbose_name='电话')),
                ('accountId', models.CharField(blank=True, default='1', help_text='用户标识', max_length=255, null=True, verbose_name='用户标识')),
                ('role', models.CharField(blank=True, default='user', help_text='角色', max_length=64, null=True, verbose_name='角色')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': '用户表',
                'verbose_name_plural': '用户表',
                'db_table': 'user_user',
                'ordering': ('-create_datetime',),
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='TableOperationLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_datetime', models.DateTimeField(auto_now_add=True, help_text='创建时间', null=True, verbose_name='创建时间')),
                ('operate_obj', models.CharField(default='未关联对象', help_text='操作对象', max_length=256, verbose_name='操作对象')),
                ('operate_des', models.CharField(default='未有操作详情', help_text='操作详情', max_length=1024, verbose_name='操作详情')),
                ('user', models.ForeignKey(blank=True, db_constraint=False, help_text='操作人员', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ruser', related_query_name='quser', to=settings.AUTH_USER_MODEL, verbose_name='操作人员')),
            ],
            options={
                'verbose_name': '用户操作日志表',
                'verbose_name_plural': '用户操作日志表',
                'db_table': 'operation_log',
                'ordering': ('-create_datetime',),
            },
        ),
    ]
