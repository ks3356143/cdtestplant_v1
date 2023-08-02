from django.db import models
from utils.models import CoreModel
from tinymce.models import HTMLField

class Project(CoreModel):
    ident = models.CharField(max_length=64, blank=True, null=True, verbose_name="项目标识",
                             help_text="项目标识")  # 后面加上unique=True
    name = models.CharField(max_length=100, blank=True, null=True, verbose_name="项目名称", help_text="项目名称")
    engin_model = models.CharField(max_length=64, blank=True, null=True, verbose_name="工程型号", help_text="工程型号")
    section_system = models.CharField(max_length=64, blank=True, null=True, verbose_name="分系统", help_text="分系统")
    sub_system = models.CharField(max_length=64, blank=True, null=True, verbose_name="子系统", help_text="子系统")
    device = models.CharField(max_length=64, blank=True, null=True, verbose_name="设备", help_text="设备")
    beginTime = models.DateField(auto_now_add=True, null=True, blank=True, help_text="开始时间", verbose_name="开始时间")
    endTime = models.DateField(auto_now_add=True, null=True, blank=True, help_text="结束时间", verbose_name="结束时间")
    duty_person = models.CharField(max_length=64, verbose_name="负责人", help_text="负责人")
    member = models.JSONField(null=True, blank=True, help_text="项目成员", verbose_name="项目成员", default=[])
    security_level = models.CharField(max_length=8, blank=True, null=True, verbose_name="安全等级", help_text="安全等级")
    test_level = models.JSONField(null=True, blank=True, help_text="测试级别", verbose_name="测试级别", default=[])
    plant_type = models.CharField(max_length=64, blank=True, null=True, verbose_name="平台类型", help_text="平台类型")
    report_type = models.CharField(max_length=64, blank=True, null=True, verbose_name="报告类型", help_text="报告类型")
    language = models.JSONField(null=True, blank=True, help_text="被测语言", verbose_name="被测语言", default=[])
    standard = models.JSONField(null=True, blank=True, help_text="依据标准", verbose_name="依据标准", default=[])
    entrust_ident = models.CharField(max_length=64, blank=True, null=True, verbose_name="委托方标识", help_text="委托方标识")
    entrust_legal = models.CharField(max_length=64, blank=True, null=True, verbose_name="委托方法人", help_text="委托方法人")
    entrust_contact = models.CharField(max_length=64, blank=True, null=True, verbose_name="委托方联系人", help_text="委托方联系人")
    entrust_contact_phone = models.CharField(max_length=64, blank=True, null=True, verbose_name="委托方电话",
                                             help_text="委托方电话")
    entrust_email = models.CharField(max_length=64, blank=True, null=True, verbose_name="委托方邮箱", help_text="委托方邮箱")
    dev_ident = models.CharField(max_length=64, blank=True, null=True, verbose_name="研制方标识", help_text="研制方标识")
    dev_legal = models.CharField(max_length=64, blank=True, null=True, verbose_name="研制方法人", help_text="研制方法人")
    dev_contact = models.CharField(max_length=64, blank=True, null=True, verbose_name="研制方联系人", help_text="研制方联系人")
    dev_contact_phone = models.CharField(max_length=64, blank=True, null=True, verbose_name="研制方电话", help_text="研制方电话")
    dev_email = models.CharField(max_length=64, blank=True, null=True, verbose_name="研制方邮箱", help_text="研制方邮箱")
    test_ident = models.CharField(max_length=64, blank=True, null=True, verbose_name="测评中心标识", help_text="测评中心标识")
    test_legal = models.CharField(max_length=64, blank=True, null=True, verbose_name="测评中心法人", help_text="测评中心法人")
    test_contact = models.CharField(max_length=64, blank=True, null=True, verbose_name="测评中心联系人", help_text="测评中心联系人")
    test_contact_phone = models.CharField(max_length=64, blank=True, null=True, verbose_name="测评中心电话",
                                          help_text="测评中心电话")
    test_email = models.CharField(max_length=64, blank=True, null=True, verbose_name="测评中心邮箱", help_text="测评中心邮箱")
    step = models.CharField(max_length=8, blank=True, null=True, verbose_name="项目阶段", help_text="项目阶段")

    class Meta:
        db_table = 'project_project'
        verbose_name = "项目信息"
        verbose_name_plural = verbose_name
        ordering = ('-create_datetime',)

class Round(CoreModel):
    ident = models.CharField(max_length=64, blank=True, null=True, verbose_name="轮次标识",
                             help_text="轮次标识")  # 后面加上unique=True
    name = models.CharField(max_length=64, blank=True, null=True, verbose_name="轮次名称",
                            help_text="轮次名称")
    beginTime = models.DateField(auto_now_add=True, null=True, blank=True, help_text="开始时间", verbose_name="开始时间")
    endTime = models.DateField(auto_now_add=True, null=True, blank=True, help_text="结束时间", verbose_name="结束时间")
    speedGrade = models.CharField(max_length=64, blank=True, null=True, verbose_name="速度等级", help_text="速度等级")
    package = models.CharField(max_length=64, blank=True, null=True, verbose_name="封装", help_text="封装")
    grade = models.CharField(max_length=64, blank=True, null=True, verbose_name="等级", help_text="等级")
    best_condition_voltage = models.CharField(max_length=64, blank=True, null=True, verbose_name="最优工况电压",
                                              help_text="最优工况电压")
    best_condition_tem = models.CharField(max_length=64, blank=True, null=True, verbose_name="最优工况温度",
                                          help_text="最优工况温度")
    typical_condition_voltage = models.CharField(max_length=64, blank=True, null=True, verbose_name="典型工况电压",
                                                 help_text="典型工况电压")
    typical_condition_tem = models.CharField(max_length=64, blank=True, null=True, verbose_name="典型工况温度",
                                             help_text="典型工况温度")
    low_condition_voltage = models.CharField(max_length=64, blank=True, null=True, verbose_name="最低工况电压",
                                             help_text="最低工况电压")
    low_condition_tem = models.CharField(max_length=64, blank=True, null=True, verbose_name="最低工况温度",
                                         help_text="最低工况温度")
    project = models.ForeignKey(to="Project", db_constraint=False, related_name="pField", on_delete=models.CASCADE,
                                verbose_name='归属项目', help_text='归属项目', related_query_name='pQuery')
    level = models.CharField(max_length=15, verbose_name='树状级别第一级', help_text="树状级别第一级", default='0')
    key = models.CharField(max_length=15, verbose_name='给前端的树状级别', help_text="给前端的树状级别")
    title = models.CharField(max_length=15, verbose_name='给前端的name', help_text="给前端的name")

    class Meta:
        db_table = 'project_round'
        verbose_name = "轮次信息"
        verbose_name_plural = verbose_name
        ordering = ('key',)

class Dut(CoreModel):
    ident = models.CharField(max_length=64, blank=True, null=True, verbose_name="被测件标识",
                             help_text="被测件标识")  # 后面加上unique=True
    type = models.CharField(max_length=16, blank=True, null=True, verbose_name="被测件类型", help_text="被测件类型")
    name = models.CharField(max_length=64, blank=True, null=True, verbose_name="被测件名称", help_text="被测件名称")
    black_line = models.CharField(max_length=64, blank=True, null=True, verbose_name="空行代码数", help_text="空行代码数")
    pure_code_line = models.CharField(max_length=64, blank=True, null=True, verbose_name="代码行数", help_text="代码行数")
    mix_line = models.CharField(max_length=64, blank=True, null=True, verbose_name="混合行数", help_text="混合行数")
    total_comment_line = models.CharField(max_length=64, blank=True, null=True, verbose_name="总注释行", help_text="总注释行")
    total_code_line = models.CharField(max_length=64, blank=True, null=True, verbose_name="总代码行", help_text="总代码行")
    total_line = models.CharField(max_length=64, blank=True, null=True, verbose_name="总行数", help_text="总行数")
    comment_line = models.CharField(max_length=64, blank=True, null=True, verbose_name="注释率", help_text="注释率")
    title = models.CharField(max_length=64, blank=True, null=True, verbose_name="树-名称", help_text="树-名称")
    key = models.CharField(max_length=64, blank=True, null=True, verbose_name="树-key", help_text="树-key")
    level = models.CharField(max_length=64, blank=True, null=True, verbose_name="树-level", help_text="树-level",
                             default=1)  # 默认为1
    project = models.ForeignKey(to="Project", db_constraint=False, related_name="pdField", on_delete=models.CASCADE,
                                verbose_name='归属项目', help_text='归属项目', related_query_name='pdQuery')
    round = models.ForeignKey(to="Round", db_constraint=False, related_name="rdField", on_delete=models.CASCADE,
                              verbose_name='归属轮次', help_text='归属轮次', related_query_name='rdQuery')

    class Meta:
        db_table = 'project_dut'
        verbose_name = "被测件信息"
        verbose_name_plural = verbose_name
        ordering = ('key',)

class Design(CoreModel):
    ident = models.CharField(max_length=64, blank=True, null=True, verbose_name="设计需求标识", help_text="设计需求标识")
    name = models.CharField(max_length=64, blank=True, null=True, verbose_name="设计需求名称", help_text="设计需求名称")
    demandType = models.CharField(max_length=8, blank=True, null=True, verbose_name="设计需求类型", help_text="设计需求类型")
    description = HTMLField(blank=True, null=True, verbose_name="设计需求描述", help_text="设计需求描述")
    title = models.CharField(max_length=64, blank=True, null=True, verbose_name="树-名称", help_text="树-名称")
    key = models.CharField(max_length=64, blank=True, null=True, verbose_name="round-dut-designkey",
                           help_text="round-dut-designkey")
    level = models.CharField(max_length=64, blank=True, null=True, verbose_name="树-level", help_text="树-level",
                             default=2)  # 默认为2
    project = models.ForeignKey(to="Project", db_constraint=False, related_name="psField", on_delete=models.CASCADE,
                                verbose_name='归属项目', help_text='归属项目', related_query_name='psQuery')
    round = models.ForeignKey(to="Round", db_constraint=False, related_name="rsField", on_delete=models.CASCADE,
                              verbose_name='归属轮次', help_text='归属轮次', related_query_name='rsQuery')
    dut = models.ForeignKey(to="Dut", db_constraint=False, related_name="rsField", on_delete=models.CASCADE,
                            verbose_name='归属轮次', help_text='归属轮次', related_query_name='rsQuery')

    class Meta:
        db_table = 'project_design'
        verbose_name = "测试需求"
        verbose_name_plural = verbose_name
        ordering = ('key',)

class TestDemand(CoreModel):
    ident = models.CharField(max_length=64, blank=True, null=True, verbose_name="测试需求标识", help_text="测试需求标识")
    name = models.CharField(max_length=64, blank=True, null=True, verbose_name="测试需求名称", help_text="测试需求名称")
    adequacy = models.CharField(max_length=128, blank=True, null=True, verbose_name="充分条件", help_text="充分条件")
    termination = models.CharField(max_length=64, blank=True, null=True, verbose_name="终止条件", help_text="终止条件")
    premise = models.CharField(max_length=64, blank=True, null=True, verbose_name="前提", help_text="前提")
    priority = models.CharField(max_length=8, blank=True, null=True, verbose_name="优先级", help_text="优先级")
    testType = models.CharField(max_length=32,null=True, blank=True, help_text="测试类型", verbose_name="测试类型",default="1")
    testMethod = models.CharField(max_length=512, blank=True, null=True, verbose_name="测试方法", help_text="测试方法")
    title = models.CharField(max_length=64, blank=True, null=True, verbose_name="树-名称", help_text="树-名称")
    key = models.CharField(max_length=64, blank=True, null=True, verbose_name="round-dut-designkey-testdemand",
                           help_text="round-dut-designkey-testdemand")
    level = models.CharField(max_length=64, blank=True, null=True, verbose_name="树-level", help_text="树-level",
                             default=3)  # 默认为3
    project = models.ForeignKey(to="Project", db_constraint=False, related_name="ptField", on_delete=models.CASCADE,
                                verbose_name='归属项目', help_text='归属项目', related_query_name='ptQuery')
    round = models.ForeignKey(to="Round", db_constraint=False, related_name="rtField", on_delete=models.CASCADE,
                              verbose_name='归属轮次', help_text='归属轮次', related_query_name='dutQuery')
    dut = models.ForeignKey(to="Dut", db_constraint=False, related_name="dutField", on_delete=models.CASCADE,
                            verbose_name='归属轮次', help_text='归属轮次', related_query_name='dtQuery')
    design = models.ForeignKey(to="Design", db_constraint=False, related_name="dtField", on_delete=models.CASCADE,
                               verbose_name='归属轮次', help_text='归属轮次', related_query_name='dtQuery')

class TestDemandContent(CoreModel):
    testXuQiu = models.CharField(max_length=1024, blank=True, null=True, verbose_name="测试需求条目", help_text="测试需求条目")
    testYuQi = models.CharField(max_length=1024, blank=True, null=True, verbose_name="测试需求条目的预期", help_text="测试需求条目的预期")
    testDemand = models.ForeignKey(to="TestDemand", db_constraint=False, related_name="testQField",
                                   on_delete=models.CASCADE, verbose_name='归属的测试项', help_text='归属的测试项',
                                   related_query_name='testQField')
