# -*- coding: utf-8 -*-
from django.db import models

class CoreModel(models.Model):
    """
    核心标准抽象模型，可直接继承使用
    增加审计字段，覆盖字段时，字段名称请勿修改，必须统一审计字段名称
    """
    id = models.BigAutoField(primary_key=True, help_text="Id", verbose_name="Id")
    remark = models.CharField(max_length=255, verbose_name="描述", null=True, blank=True, help_text="描述")
    update_datetime = models.DateField(auto_now=True, null=True, blank=True, help_text="修改时间", verbose_name="修改时间")
    create_datetime = models.DateField(auto_now_add=True, null=True, blank=True, help_text="创建时间",
                                       verbose_name="创建时间")
    sort = models.IntegerField(default=1, null=True, blank=True, verbose_name="显示排序", help_text="显示排序")

    class Meta:
        abstract = True  # 指定为True不会创建表，只会当做父类
        verbose_name = '核心模型'
        verbose_name_plural = verbose_name
