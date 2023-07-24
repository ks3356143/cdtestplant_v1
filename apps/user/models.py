from django.contrib.auth.models import AbstractUser
from django.db import models
from utils.models import CoreModel

STATUS_CHOICES = (
    (0, '禁用'),
    (1, '启用')
)

class Users(AbstractUser, CoreModel):
    username = models.CharField(max_length=150, unique=True, db_index=True, verbose_name='用户账号', help_text="用户账号")
    name = models.CharField(max_length=40, verbose_name="姓名", help_text="姓名")
    avatar = models.TextField(verbose_name="头像", null=True, blank=True, help_text="头像")
    email = models.EmailField(max_length=255, verbose_name="邮箱", null=True, blank=True, help_text="邮箱")
    status = models.CharField(max_length=15, verbose_name='启用状态', help_text="status")
    job = models.CharField(max_length=255, verbose_name='工作', null=True, blank=True, help_text='工作')
    jobName = models.CharField(max_length=255, verbose_name='工作名称', null=True, blank=True, help_text='工作名称')
    organization = models.CharField(max_length=255, verbose_name='工作组织', null=True, blank=True, help_text='工作组织')
    location = models.CharField(max_length=255, verbose_name='住地', null=True, blank=True, help_text='住地')
    locationName = models.CharField(max_length=255, verbose_name='住地名称', null=True, blank=True, help_text='住地名称')
    introduction = models.CharField(max_length=255, verbose_name='自我介绍', null=True, blank=True, help_text='自我介绍')
    personalWebsite = models.CharField(max_length=255, verbose_name='个人网站', null=True, blank=True, help_text='个人网站')
    phone = models.CharField(max_length=255, verbose_name="电话", null=True, blank=True, help_text="电话")
    accountId = models.CharField(max_length=255, verbose_name="电话", null=True, blank=True, help_text="电话")
    role = models.CharField(max_length=64, verbose_name="角色", null=True, blank=True, help_text="角色")

    class Meta:
        db_table = 'user_user'
        verbose_name = '用户表'
        verbose_name_plural = verbose_name
        ordering = ('-create_datetime',)
