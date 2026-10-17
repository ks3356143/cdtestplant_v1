from django.db import models
from cdtestplant_v1 import settings

class LoginLog(models.Model):
    id = models.BigAutoField(primary_key=True, help_text="Id", verbose_name="Id")
    remark = models.CharField(max_length=255, verbose_name="描述", null=True, blank=True, help_text="描述")
    creator = models.ForeignKey(to=settings.AUTH_USER_MODEL, related_query_name='creator_query', null=True,
                                verbose_name='创建人', help_text="创建人", on_delete=models.SET_NULL, db_constraint=False)
    modifier = models.CharField(max_length=255, null=True, blank=True, help_text="修改人", verbose_name="修改人")
    LOGIN_TYPE_CHOICES = (
        (1, '普通登录'),
    )
    username = models.CharField(max_length=32, verbose_name="登录用户名", null=True, blank=True, help_text="登录用户名")
    ip = models.CharField(max_length=32, verbose_name="登录ip", null=True, blank=True, help_text="登录ip")
    agent = models.TextField(verbose_name="agent信息", null=True, blank=True, help_text="agent信息")
    browser = models.CharField(max_length=200, verbose_name="浏览器名", null=True, blank=True, help_text="浏览器名")
    os = models.CharField(max_length=200, verbose_name="操作系统", null=True, blank=True, help_text="操作系统")
    country = models.CharField(max_length=50, verbose_name="国家", null=True, blank=True, help_text="国家")
    login_type = models.IntegerField(default=1, choices=LOGIN_TYPE_CHOICES, verbose_name="登录类型",
                                     help_text="登录类型")
    update_datetime = models.DateTimeField(auto_now=True, null=True, blank=True, help_text="修改时间", verbose_name="修改时间")
    create_datetime = models.DateTimeField(auto_now_add=True, null=True, blank=True, help_text="创建时间",
                                           verbose_name="创建时间")
    sort = models.IntegerField(default=1, null=True, blank=True, verbose_name="显示排序", help_text="显示排序")

    class Meta:
        db_table = 'system_login_log'
        verbose_name = '登录日志'
        verbose_name_plural = verbose_name
        ordering = ('-create_datetime',)

class OperationLog(models.Model):
    id = models.BigAutoField(primary_key=True, help_text="Id", verbose_name="Id")
    remark = models.CharField(max_length=255, verbose_name="描述", null=True, blank=True, help_text="描述")
    creator = models.ForeignKey(to=settings.AUTH_USER_MODEL, related_query_name='creator_query', null=True,
                                verbose_name='创建人', help_text="创建人", on_delete=models.SET_NULL, db_constraint=False)
    modifier = models.CharField(max_length=255, null=True, blank=True, help_text="修改人", verbose_name="修改人")
    request_username = models.CharField(max_length=50, blank=True, null=True, verbose_name="请求用户",
                                        help_text="请求用户")
    request_modular = models.CharField(max_length=64, verbose_name="请求模块", null=True, blank=True,
                                       help_text="请求模块")
    request_path = models.CharField(max_length=400, verbose_name="请求地址", null=True, blank=True,
                                    help_text="请求地址")
    request_body = models.TextField(verbose_name="请求参数", null=True, blank=True, help_text="请求参数")
    request_method = models.CharField(max_length=8, verbose_name="请求方式", null=True, blank=True,
                                      help_text="请求方式")
    request_msg = models.TextField(verbose_name="操作说明", null=True, blank=True, help_text="操作说明")
    request_ip = models.CharField(max_length=32, verbose_name="请求ip地址", null=True, blank=True,
                                  help_text="请求ip地址")
    request_browser = models.CharField(max_length=64, verbose_name="请求浏览器", null=True, blank=True,
                                       help_text="请求浏览器")
    response_code = models.CharField(max_length=32, verbose_name="响应状态码", null=True, blank=True,
                                     help_text="响应状态码")
    request_os = models.CharField(max_length=64, verbose_name="操作系统", null=True, blank=True, help_text="操作系统")
    json_result = models.TextField(verbose_name="返回信息", null=True, blank=True, help_text="返回信息")
    status = models.BooleanField(default=False, verbose_name="响应状态", help_text="响应状态")
    update_datetime = models.DateTimeField(auto_now=True, null=True, blank=True, help_text="修改时间", verbose_name="修改时间")
    create_datetime = models.DateTimeField(auto_now_add=True, null=True, blank=True, help_text="创建时间",
                                           verbose_name="创建时间")
    sort = models.IntegerField(default=1, null=True, blank=True, verbose_name="显示排序", help_text="显示排序")

    class Meta:
        db_table = 'system_operation_log'
        verbose_name = '操作日志'
        verbose_name_plural = verbose_name
        ordering = ('-create_datetime',)


class AuditLog(models.Model):
    """统一审计日志（GB/T 28452-2012 第三级 7.1.6）：核心安全事件全程留痕，仅审计员可查，防篡改（无更新入口）"""
    id = models.BigAutoField(primary_key=True, help_text="Id", verbose_name="Id")
    username = models.CharField(max_length=50, verbose_name="主体账号", null=True, blank=True,
                                help_text="事件主体账号")
    role = models.CharField(max_length=30, verbose_name="主体角色", null=True, blank=True,
                            help_text="事件主体角色")
    actor = models.ForeignKey(to=settings.AUTH_USER_MODEL, related_query_name='audit_actor', null=True,
                              verbose_name='主体用户', help_text="事件主体用户", on_delete=models.SET_NULL,
                              db_constraint=False)
    event_type = models.CharField(max_length=40, verbose_name="事件类型", help_text="EVENT_* 常量")
    detail = models.CharField(max_length=500, verbose_name="事件内容", help_text="事件描述")
    success = models.BooleanField(default=True, verbose_name="操作结果", help_text="成功/失败")
    ip = models.CharField(max_length=32, verbose_name="操作IP", null=True, blank=True, help_text="操作IP")
    user_agent = models.CharField(max_length=500, verbose_name="设备信息", null=True, blank=True,
                                  help_text="User-Agent")
    create_datetime = models.DateTimeField(auto_now_add=True, null=True, blank=True, help_text="事件时间",
                                           verbose_name="事件时间")

    class Meta:
        db_table = 'system_audit_log'
        verbose_name = '统一审计日志'
        verbose_name_plural = verbose_name
        ordering = ('-create_datetime',)
        indexes = (
            models.Index(fields=['create_datetime'], name='auditlog_time_idx'),
            models.Index(fields=['event_type'], name='auditlog_type_idx'),
        )


class DataIntegrityTag(models.Model):
    """数据完整性校验标签（GB/T 28452-2012 第三级 7.1.7）：重要敏感数据的关键字段快照摘要，
    业务写操作后刷新；核查时重算比对，不一致即完整性破损（多为绕过应用直改数据库）"""
    id = models.BigAutoField(primary_key=True, help_text="Id", verbose_name="Id")
    table_name = models.CharField(max_length=64, verbose_name="受保护表",
                                  help_text="project_case 等 db_table")
    object_id = models.CharField(max_length=32, verbose_name="数据行 id")
    digest = models.CharField(max_length=64, verbose_name="完整性摘要(SHA256)",
                              help_text="关键字段排序 JSON 快照的 SHA256")
    algorithm = models.CharField(max_length=16, default='SHA256', verbose_name="算法")
    update_datetime = models.DateTimeField(auto_now=True, null=True, blank=True,
                                           verbose_name="标签更新时间")
    create_datetime = models.DateTimeField(auto_now_add=True, null=True, blank=True,
                                           verbose_name="创建时间")

    class Meta:
        db_table = 'system_data_integrity_tag'
        verbose_name = '数据完整性标签'
        verbose_name_plural = verbose_name
        unique_together = (('table_name', 'object_id'),)

    def __str__(self):
        return f'完整性标签[{self.table_name}#{self.object_id}]'


class SecurityPolicy(models.Model):
    """系统安全策略（单例行，由系统安全员 secadmin 维护）——三权分立之安全员职责载体"""
    login_max_attempts = models.IntegerField(default=5, verbose_name="登录失败最大尝试次数",
                                             help_text="超过该次数触发账号锁定")
    login_window_minutes = models.IntegerField(default=15, verbose_name="失败统计时间窗口（分钟）",
                                               help_text="在该时间窗口内累计失败次数")
    login_lock_minutes = models.IntegerField(default=30, verbose_name="账号锁定时长（分钟）",
                                             help_text="触发锁定后禁止登录的时长")
    update_datetime = models.DateTimeField(auto_now=True, null=True, blank=True, verbose_name="更新时间")

    class Meta:
        db_table = 'system_security_policy'
        verbose_name = '系统安全策略'

    def __str__(self):
        return f'安全策略：失败{self.login_max_attempts}次/{self.login_window_minutes}分钟锁定{self.login_lock_minutes}分钟'

    @classmethod
    def load(cls):
        """取单例策略行，不存在则按默认值创建"""
        obj = cls.objects.first()
        if obj is None:
            obj = cls.objects.create()
        return obj
