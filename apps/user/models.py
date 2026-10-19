from django.contrib.auth.models import AbstractUser
from django.db import models
from utils.crypto import EncryptedCharField, blind_index
from utils.models import CoreModel

class Users(AbstractUser, CoreModel):
    username = models.CharField(max_length=150, unique=True, db_index=True, verbose_name='用户账号',
                                help_text="用户账号")
    name = models.CharField(max_length=40, verbose_name="姓名", help_text="姓名")
    avatar = models.TextField(verbose_name="头像", null=True, blank=True, help_text="头像")
    status = models.CharField(max_length=15, verbose_name='启用状态', help_text="status", default='1')
    job = models.CharField(max_length=255, verbose_name='工作', null=True, blank=True, help_text='工作')
    jobName = models.CharField(max_length=255, verbose_name='工作名称', null=True, blank=True, help_text='工作名称')
    organization = models.CharField(max_length=255, verbose_name='工作组织', null=True, blank=True,
                                    help_text='工作组织')
    location = models.CharField(max_length=255, verbose_name='住地', null=True, blank=True, help_text='住地')
    locationName = models.CharField(max_length=255, verbose_name='住地名称', null=True, blank=True,
                                    help_text='住地名称')
    introduction = models.CharField(max_length=255, verbose_name='自我介绍', null=True, blank=True,
                                    help_text='自我介绍')
    personalWebsite = models.CharField(max_length=255, verbose_name='个人网站', null=True, blank=True,
                                       help_text='个人网站')
    phone = EncryptedCharField(max_length=255, verbose_name="电话", null=True, blank=True,
                               help_text="电话（落库加密，7.1.8 用户数据保密性保护）", default='18888888888')
    # 电话的 SHA-256 盲索引：加密后不能做 LIKE 模糊检索，用等值索引支撑"按电话查用户"
    phone_index = models.CharField(max_length=64, verbose_name="电话盲索引", null=True, blank=True, default='',
                                   db_index=True, help_text="电话 SHA-256 盲索引，仅用于等值检索")
    # 邮箱同样属于用户重要数据，落库加密（覆盖 AbstractUser 的明文 EmailField）
    email = EncryptedCharField(max_length=255, verbose_name="邮箱", null=True, blank=True,
                               help_text="邮箱（落库加密，7.1.8 用户数据保密性保护）")
    accountId = models.CharField(max_length=255, verbose_name="用户标识", null=True, blank=True, help_text="用户标识", default='1')
    # 主体敏感标记：用户可访问的最高密级许可（GB/T 28452 7.1.4），由系统管理员配置
    clearance = models.CharField(max_length=30, verbose_name="密级许可", help_text="可访问的最高密级", default='1')
    # 三权分立角色：admin 系统管理员 / secadmin 系统安全员 / auditadmin 系统审计员 / user 普通用户
    role = models.CharField(
        max_length=64, verbose_name="角色", null=True, blank=True, help_text="角色", default='user',
        choices=(('admin', '系统管理员'), ('secadmin', '系统安全员'), ('auditadmin', '系统审计员'), ('user', '普通用户'))
    )

    def save(self, *args, **kwargs):
        # 维护电话盲索引：加密列无法 LIKE，改由 SHA-256 等值索引支撑检索（7.1.8）
        self.phone_index = blind_index(self.phone)
        update_fields = kwargs.get('update_fields')
        if update_fields is not None and 'phone_index' not in update_fields:
            kwargs['update_fields'] = list(update_fields) + ['phone_index']
        super().save(*args, **kwargs)

    def __str__(self):
        return f'用户账号:{self.username}-用户名:{self.name}'

    class Meta:
        db_table = 'user_user'
        verbose_name = '用户表'
        verbose_name_plural = verbose_name
        ordering = ('-create_datetime',)

class TableOperationLog(models.Model):
    create_datetime = models.DateTimeField(auto_now_add=True, null=True, blank=True, help_text="创建时间",
                                           verbose_name="创建时间")
    user = models.ForeignKey(to="Users", db_constraint=False, related_name="ruser", on_delete=models.CASCADE,
                             verbose_name='操作人员', help_text='操作人员', related_query_name='quser', null=True,
                             blank=True)
    # 2.操作的对象
    operate_obj = models.CharField(max_length=256, verbose_name='操作对象', default='未关联对象', help_text='操作对象')
    # 3.操作详情
    operate_des = models.CharField(max_length=1024, verbose_name='操作详情', default='未有操作详情',
                                   help_text='操作详情')

    class Meta:
        db_table = 'operation_log'
        verbose_name = '用户操作日志表'
        verbose_name_plural = verbose_name
        ordering = ('-create_datetime',)
