from django.contrib.auth.models import AbstractUser, Group
from django.db import models
from utils.models import CoreModel

STATUS_CHOICES = (
    (0, '禁用'),
    (1, '启用')
)

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
    phone = models.CharField(max_length=255, verbose_name="电话", null=True, blank=True, help_text="电话", default='18888888888')
    accountId = models.CharField(max_length=255, verbose_name="用户标识", null=True, blank=True, help_text="用户标识", default='1')
    role = models.CharField(max_length=64, verbose_name="角色", null=True, blank=True, help_text="角色", default='user')

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
