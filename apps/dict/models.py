from django.db import models
from utils.models import CoreModel

# Create your models here.
## 字典以及字典item
class Dict(CoreModel):
    name = models.CharField(max_length=100, blank=True, null=True, verbose_name="字典名称", help_text="字典名称")
    code = models.CharField(max_length=100, blank=True, null=True, verbose_name="编码", help_text="编码")
    status = models.BooleanField(default=True, blank=True, verbose_name="状态", help_text="状态")
    remark = models.CharField(max_length=2000, blank=True, null=True, verbose_name="备注", help_text="备注")

    class Meta:
        db_table = 'system_dict'
        verbose_name = "字典表"
        verbose_name_plural = verbose_name
        ordering = ('-create_datetime',)

class DictItem(CoreModel):
    title = models.CharField(max_length=100, blank=True, null=True, verbose_name="显示名称", help_text="显示名称")
    key = models.CharField(max_length=100, blank=True, null=True, verbose_name="实际值", help_text="实际值")
    status = models.BooleanField(default=True, blank=True, verbose_name="状态", help_text="状态")
    dict = models.ForeignKey(to="Dict", db_constraint=False, related_name="dictItem", on_delete=models.CASCADE,
                             help_text="字典")
    remark = models.CharField(max_length=2000, blank=True, null=True, verbose_name="备注", help_text="备注")

    class Meta:
        db_table = 'system_dict_item'
        verbose_name = "字典表item表"
        verbose_name_plural = verbose_name
        ordering = ('-create_datetime',)