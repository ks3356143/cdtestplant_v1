from django.db import models
from utils.models import CoreModel
from tinymce.models import HTMLField
from shortuuidfield import ShortUUIDField

def create_list():
    return []

def create_list_1():
    return ['1']

class Project(CoreModel):
    objects = models.Manager()
    ident = models.CharField(max_length=64, blank=True, null=True, verbose_name="项目标识",
                             help_text="项目标识", unique=True)  # 唯一
    name = models.CharField(max_length=100, blank=True, null=True, verbose_name="项目名称", help_text="项目名称")
    beginTime = models.DateField(auto_now_add=True, null=True, blank=True, help_text="开始时间",
                                 verbose_name="开始时间")
    endTime = models.DateField(auto_now_add=True, null=True, blank=True, help_text="结束时间", verbose_name="结束时间")
    duty_person = models.CharField(max_length=64, verbose_name="负责人", help_text="负责人")
    member = models.JSONField(null=True, blank=True, help_text="项目成员", verbose_name="项目成员", default=create_list)
    # 8月新增字段
    quality_person = models.CharField(max_length=64, verbose_name="质量保证员", help_text="质量保证员")
    vise_person = models.CharField(max_length=64, verbose_name="质量监督员", help_text="质量监督员")
    config_person = models.CharField(max_length=64, verbose_name="配置管理员", help_text="配置管理员")
    # ~~~~~~~~~~~
    security_level = models.CharField(max_length=8, blank=True, null=True, verbose_name="安全等级",
                                      help_text="安全等级")
    test_level = models.JSONField(null=True, blank=True, help_text="测试级别", verbose_name="测试级别",
                                  default=create_list)
    plant_type = models.JSONField(null=True, blank=True, help_text="平台类型", verbose_name="平台类型",
                                  default=create_list)
    report_type = models.CharField(max_length=64, blank=True, null=True, verbose_name="报告类型", help_text="报告类型")
    language = models.JSONField(null=True, blank=True, help_text="被测语言", verbose_name="被测语言",
                                default=create_list)
    standard = models.JSONField(null=True, blank=True, help_text="依据标准", verbose_name="依据标准",
                                default=create_list)
    entrust_unit = models.CharField(max_length=64, verbose_name="委托方单位", help_text="委托方单位")
    entrust_contact = models.CharField(max_length=64, blank=True, null=True, verbose_name="委托方联系人",
                                       help_text="委托方联系人")
    entrust_contact_phone = models.CharField(max_length=64, blank=True, null=True, verbose_name="委托方电话",
                                             help_text="委托方电话")
    entrust_email = models.CharField(max_length=64, blank=True, null=True, verbose_name="委托方邮箱",
                                     help_text="委托方邮箱")
    dev_unit = models.CharField(max_length=64, verbose_name="开发方单位", help_text="开发方单位")
    dev_contact = models.CharField(max_length=64, blank=True, null=True, verbose_name="研制方联系人",
                                   help_text="研制方联系人")
    dev_contact_phone = models.CharField(max_length=64, blank=True, null=True, verbose_name="研制方电话",
                                         help_text="研制方电话")
    dev_email = models.CharField(max_length=64, blank=True, null=True, verbose_name="研制方邮箱",
                                 help_text="研制方邮箱")
    test_unit = models.CharField(max_length=64, verbose_name="测试方单位", help_text="测试方单位")
    test_contact = models.CharField(max_length=64, blank=True, null=True, verbose_name="测评中心联系人",
                                    help_text="测评中心联系人")
    test_contact_phone = models.CharField(max_length=64, blank=True, null=True, verbose_name="测评中心电话",
                                          help_text="测评中心电话")
    test_email = models.CharField(max_length=64, blank=True, null=True, verbose_name="测评中心邮箱",
                                  help_text="测评中心邮箱")
    step = models.CharField(max_length=8, blank=True, null=True, verbose_name="项目阶段", help_text="项目阶段")
    abbreviation = models.JSONField(null=True, blank=True, help_text="缩略语", verbose_name="缩略语",
                                    default=create_list)
    soft_type = models.SmallIntegerField(verbose_name='软件类型', choices=((1, '新研'), (2, '改造'), (3, '沿用')),
                                         default=1)
    runtime = models.CharField(max_length=8, blank=True, null=True, verbose_name="运行环境",
                               help_text="运行环境")
    devplant = models.CharField(max_length=8, blank=True, null=True, verbose_name="开发环境",
                                help_text="开发环境")
    # 9月2日新增字段：密级
    secret = models.CharField(max_length=30, default='1', verbose_name='密级', help_text='密级')

    def __str__(self):
        return f'项目{self.ident}-{self.name}'

    class Meta:
        db_table = 'project_project'
        verbose_name = "项目信息"
        verbose_name_plural = verbose_name
        ordering = ('-create_datetime',)

class Round(CoreModel):
    objects = models.Manager()
    ident = models.CharField(max_length=64, blank=True, null=True, verbose_name="轮次标识",
                             help_text="轮次标识")  # 后面加上unique=True
    name = models.CharField(max_length=64, blank=True, null=True, verbose_name="轮次名称",
                            help_text="轮次名称")
    beginTime = models.DateField(auto_now_add=True, null=True, blank=True, help_text="开始时间",
                                 verbose_name="开始时间")
    endTime = models.DateField(auto_now_add=True, null=True, blank=True, help_text="结束时间", verbose_name="结束时间")
    grade = models.CharField(max_length=64, blank=True, null=True, verbose_name="等级", help_text="等级", default='1')
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
    # 新增执行地点
    location = models.CharField(max_length=30, verbose_name='测评执行地点', help_text='测评执行地点')

    def __str__(self):
        return f'第{str(int(self.key) + 1)}轮次'

    class Meta:
        db_table = 'project_round'
        verbose_name = "轮次信息"
        verbose_name_plural = verbose_name
        ordering = ('key',)

class Dut(CoreModel):
    objects = models.Manager()
    ident = models.CharField(max_length=64, blank=True, null=True, verbose_name="被测件标识",
                             help_text="被测件标识")  # 后面加上unique=True
    type = models.CharField(max_length=16, blank=True, null=True, verbose_name="被测件类型", help_text="被测件类型")
    name = models.CharField(max_length=64, blank=True, null=True, verbose_name="被测件名称", help_text="被测件名称")
    # 2025年4月28日更新，分为总函数、有效代码行数、注释行数
    total_lines = models.CharField(max_length=64, blank=True, null=True, verbose_name='总行数')
    effective_lines = models.CharField(max_length=64, blank=True, null=True, verbose_name='有效代码行数')
    comment_lines = models.CharField(max_length=64, blank=True, null=True, verbose_name='注释行数')

    # 更新结束
    title = models.CharField(max_length=64, blank=True, null=True, verbose_name="树-名称", help_text="树-名称")
    key = models.CharField(max_length=64, blank=True, null=True, verbose_name="树-key", help_text="树-key")
    # 被测件添加版本、发布单位、发布时间
    version = models.CharField(max_length=64, blank=True, null=True, verbose_name="发布版本", help_text="发布版本")
    release_union = models.CharField(max_length=64, blank=True, null=True, verbose_name="发布版本",
                                     help_text="发布版本")
    release_date = models.DateField(auto_now_add=True, null=True, blank=True, help_text="发布时间",
                                    verbose_name="发布时间")
    # 新增用户文档的编号
    ref = models.CharField(max_length=32, blank=True, null=True, verbose_name="文档编号", help_text="文档编号")
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    level = models.CharField(max_length=64, blank=True, null=True, verbose_name="树-level", help_text="树-level",
                             default=1)  # 默认为1
    project = models.ForeignKey(to="Project", db_constraint=False, related_name="pdField", on_delete=models.CASCADE,
                                verbose_name='归属项目', help_text='归属项目', related_query_name='pdQuery')
    round = models.ForeignKey(to="Round", db_constraint=False, related_name="rdField", on_delete=models.CASCADE,
                              verbose_name='归属轮次', help_text='归属轮次', related_query_name='rdQuery')

    def __str__(self):
        return f'被测件:{self.name}'

    class Meta:
        db_table = 'project_dut'
        verbose_name = "被测件信息"
        verbose_name_plural = verbose_name
        ordering = ('key',)

class DutMetrics(models.Model):
    objects = models.Manager()
    id = ShortUUIDField(primary_key=True, help_text="id", verbose_name="id")
    # 外键Dut，一个Dut储存一个指标
    dut = models.OneToOneField(Dut, on_delete=models.CASCADE, related_name='metrics', related_query_name='metrics',
                               db_constraint=False, verbose_name='归属源代码被测件')
    avg_function_lines = models.IntegerField(verbose_name='平均模块大小')
    avg_cyclomatic = models.IntegerField(verbose_name='平均圈复杂度')
    avg_fan_out = models.IntegerField(verbose_name='平均扇出数')
    function_count = models.IntegerField(verbose_name='模块数量')
    max_cyclomatic = models.IntegerField(verbose_name='最大圈复杂度')
    high_cyclomatic_ratio = models.IntegerField(verbose_name='圈复杂度>20模块占比')
    total_blanks = models.IntegerField(verbose_name='空行数')

class Design(CoreModel):
    objects = models.Manager()
    ident = models.CharField(max_length=64, blank=True, null=True, verbose_name="设计需求标识",
                             help_text="设计需求标识")
    name = models.CharField(max_length=64, blank=True, null=True, verbose_name="设计需求名称", help_text="设计需求名称")
    demandType = models.CharField(max_length=8, blank=True, null=True, verbose_name="设计需求类型",
                                  help_text="设计需求类型")
    description = HTMLField(blank=True, null=True, verbose_name="设计需求描述", help_text="设计需求描述")
    title = models.CharField(max_length=64, blank=True, null=True, verbose_name="树-名称", help_text="树-名称")
    key = models.CharField(max_length=64, blank=True, null=True, verbose_name="round-dut-designkey",
                           help_text="round-dut-designkey")
    level = models.CharField(max_length=64, blank=True, null=True, verbose_name="树-level", help_text="树-level",
                             default=2)  # 默认为2
    chapter = models.CharField(max_length=64, blank=True, verbose_name="设计需求章节号", help_text="设计需求章节号")
    project = models.ForeignKey(to="Project", db_constraint=False, related_name="psField", on_delete=models.CASCADE,
                                verbose_name='归属项目', help_text='归属项目', related_query_name='psQuery')
    round = models.ForeignKey(to="Round", db_constraint=False, related_name="dsField", on_delete=models.CASCADE,
                              verbose_name='归属轮次', help_text='归属轮次', related_query_name='rsQuery')
    dut = models.ForeignKey(to="Dut", db_constraint=False, related_name="rsField", on_delete=models.CASCADE,
                            verbose_name='归属轮次', help_text='归属轮次', related_query_name='rsQuery')
    # 如果是demandTye='3'则加上如下字段
    source = models.CharField(max_length=64, blank=True, null=True, default='', verbose_name='接口来源',
                              help_text='接口来源')
    to = models.CharField(max_length=64, blank=True, null=True, default='', verbose_name='接口目的地',
                          help_text='接口目的地')
    type = models.CharField(max_length=64, blank=True, null=True, default='', verbose_name='接口类型',
                            help_text='接口类型')
    # 注意：该字段改为接口数据
    protocal = models.CharField(max_length=64, blank=True, null=True, default='', verbose_name='接口数据',
                                help_text='接口数据')

    def __str__(self):
        return f'设计需求:{self.name}'

    class Meta:
        db_table = 'project_design'
        verbose_name = "测试需求"
        verbose_name_plural = verbose_name
        ordering = ('key',)

class TestDemand(CoreModel):
    objects = models.Manager()
    """测试项"""
    ident = models.CharField(max_length=64, blank=True, null=True, verbose_name="测试需求标识",
                             help_text="测试需求标识")
    name = models.CharField(max_length=64, blank=True, null=True, verbose_name="测试需求名称", help_text="测试需求名称")
    adequacy = models.CharField(max_length=256, blank=True, null=True, verbose_name="充分条件", help_text="充分条件")
    priority = models.CharField(max_length=8, blank=True, null=True, verbose_name="优先级", help_text="优先级")
    testType = models.CharField(max_length=8, null=True, blank=True, help_text="测试类型", verbose_name="测试类型",
                                default="1")
    testMethod = models.JSONField(blank=True, help_text="测试方法", verbose_name="测试方法", default=create_list)
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
                            verbose_name='归属被测件', help_text='归属被测件', related_query_name='dtQuery')
    design = models.ForeignKey(to="Design", db_constraint=False, related_name="dtField", on_delete=models.CASCADE,
                               verbose_name='归属设计需求', help_text='归属设计需求', related_query_name='dtQuery')
    otherDesign = models.ManyToManyField(to="Design", db_constraint=False, related_name="odField",
                                         related_query_name='odQuery', blank=True)
    # 新模版要求：测试项描述对整个测试项进行描述
    testDesciption = models.CharField(max_length=1024, blank=True, null=True, verbose_name='测试项描述', default="",
                                      help_text='测试项描述')

    def __str__(self):
        return f'测试项:{self.name}'

class TestDemandContent(CoreModel):
    objects = models.Manager()
    """测试方法中的测试子项内容"""
    testDemand = models.ForeignKey(to="TestDemand", db_constraint=False, related_name="testQField",
                                   on_delete=models.CASCADE, verbose_name='归属的测试项', help_text='归属的测试项',
                                   related_query_name='testQField')
    # 2025年4月16日去掉subDesc、condition、observe
    # 4月17日修改：因为新增步骤所以把operation和expect弄到下面Model里面了，新增字段
    subName = models.CharField(max_length=1024, blank=True, null=True, verbose_name='测试子项名称')

    def __str__(self):
        return f'测试子项:{self.subName}'

# 4月17日新增：因为测试项需要测试子项step
class TestDemandContentStep(CoreModel):
    objects = models.Manager()
    id = ShortUUIDField(primary_key=True, help_text="Id", verbose_name="Id")
    operation = models.CharField(max_length=3072, blank=True, null=True, verbose_name='测试子项操作')
    expect = models.CharField(max_length=1024, blank=True, null=True, verbose_name='期望')
    testDemandContent = models.ForeignKey(to="TestDemandContent", db_constraint=False, related_name="testStepField",
                                          on_delete=models.CASCADE, verbose_name='归属的测试项',
                                          help_text='归属的测试项',
                                          related_query_name='testStepField')

class Case(CoreModel):
    objects = models.Manager()
    ident = models.CharField(max_length=64, blank=True, null=True, verbose_name="用例标识", help_text="用例标识")
    name = models.CharField(max_length=64, blank=True, null=True, verbose_name="用例名称", help_text="用例名称")
    initialization = models.CharField(max_length=128, blank=True, null=True, verbose_name="初始条件",
                                      help_text="初始化条件")
    premise = models.CharField(max_length=128, blank=True, null=True, verbose_name="前提和约束", help_text="前提和约束")
    summarize = models.CharField(max_length=256, blank=True, null=True, verbose_name="用例综述", help_text="用例综述")
    designPerson = models.CharField(max_length=16, blank=True, null=True, verbose_name="设计人员", help_text="设计人员")
    testPerson = models.CharField(max_length=16, blank=True, null=True, verbose_name="测试人员", help_text="测试人员")
    monitorPerson = models.CharField(max_length=16, blank=True, null=True, verbose_name="审核人员",
                                     help_text="审核人员")
    project = models.ForeignKey(to="Project", db_constraint=False, related_name="pcField", on_delete=models.CASCADE,
                                verbose_name='归属项目', help_text='归属项目', related_query_name='pcQuery')
    isLeaf = models.BooleanField(default=True, verbose_name="树状图最后一个节点", help_text="树状图最后一个节点")
    round = models.ForeignKey(to="Round", db_constraint=False, related_name="rcField", on_delete=models.CASCADE,
                              verbose_name='归属轮次', help_text='归属轮次', related_query_name='rcQuery')
    dut = models.ForeignKey(to="Dut", db_constraint=False, related_name="ducField", on_delete=models.CASCADE,
                            verbose_name='归属被测件', help_text='归属被测件', related_query_name='ducQuery')
    design = models.ForeignKey(to="Design", db_constraint=False, related_name="dcField", on_delete=models.CASCADE,
                               verbose_name='归属设计需求', help_text='归属设计需求', related_query_name='dcQuery')
    test = models.ForeignKey(to="TestDemand", db_constraint=False, related_name="tcField", on_delete=models.CASCADE,
                             verbose_name='归属测试需求', help_text='归属测试需求', related_query_name='tcQuery')
    title = models.CharField(max_length=64, blank=True, null=True, verbose_name="树-名称", help_text="树-名称")
    key = models.CharField(max_length=64, blank=True, null=True, verbose_name="round-dut-designkey-testdemand-case",
                           help_text="round-dut-designkey-testdemand-case")
    level = models.CharField(max_length=64, blank=True, null=True, verbose_name="树-level", help_text="树-level",
                             default=4)  # 默认为4
    # 2024年5月31日新增属性：执行时间
    exe_time = models.DateField(blank=True, null=True, verbose_name='执行时间', help_text='执行时间')
    # 2025年4月24日新增属性：FPGA的时序图
    timing_diagram = HTMLField(blank=True, null=True, verbose_name="FPGA时序图", help_text="FPGA时序图")

    def __str__(self):
        return f'测试用例:{self.name}'

    class Meta:
        db_table = 'project_case'
        verbose_name = "测试用例"
        verbose_name_plural = verbose_name
        ordering = ('key',)

class CaseStep(CoreModel):
    objects = models.Manager()
    operation = HTMLField(blank=True, null=True, verbose_name="测试步骤-操作", help_text="测试步骤-操作")
    expect = models.CharField(max_length=3072, blank=True, null=True, verbose_name="用例预期", help_text="用例预期")
    result = HTMLField(blank=True, null=True, verbose_name="测试步骤-结果", help_text="测试步骤-结果")
    passed = models.CharField(max_length=8, null=True, blank=True, help_text="是否通过", verbose_name="是否通过",
                              default="3")
    # status = models.CharField(max_length=8, null=True, blank=True, help_text="执行状态", verbose_name="执行状态",
    #                           default="3")
    case = models.ForeignKey(to="Case", db_constraint=False, related_name="step",
                             on_delete=models.CASCADE, verbose_name='归属的测试用例', help_text='归属的测试用例',
                             related_query_name='stepQ')

    def __str__(self):
        return f'测试用例步骤'

class Problem(CoreModel):
    objects = models.Manager()
    # ident为PT_RXXXX_ident，这里需要根据测试项类型进行排序处理
    ident = models.CharField(max_length=64, blank=True, null=True, verbose_name="问题单标识", help_text="问题单标识")
    name = models.CharField(max_length=64, blank=True, null=True, verbose_name="问题单名称", help_text="问题单名称")
    # 问题状态1-已闭环 2-开放 3-推迟 4-撤销
    status = models.CharField(max_length=8, blank=True, null=True, verbose_name="缺陷状态", help_text="缺陷状态")
    # 问题等级1-一般 2-严重 3-建议 4-重大
    grade = models.CharField(max_length=8, blank=True, null=True, verbose_name="缺陷等级", help_text="缺陷等级")
    # 问题类型1-其他问题 2-文档问题 3-程序问题 4-设计问题 5-需求问题 6-数据问题
    type = models.CharField(max_length=8, blank=True, null=True, verbose_name="缺陷类型", help_text="缺陷类型")
    closeMethod = models.JSONField(null=True, blank=True, help_text="闭环方式", verbose_name="闭环方式",
                                   default=create_list_1)
    operation = HTMLField(blank=True, null=True, verbose_name="问题描述", help_text="问题描述")
    result = HTMLField(blank=True, null=True, verbose_name="问题结果/影响", help_text="问题结果/影响")
    postPerson = models.CharField(max_length=16, blank=True, null=True, verbose_name="提出人员", help_text="提出人员")
    postDate = models.DateField(auto_now_add=True, null=True, blank=True, help_text="提单日期", verbose_name="提单日期")
    designerPerson = models.CharField(max_length=16, blank=True, null=True, verbose_name="开发人员",
                                      help_text="开发人员")
    designDate = models.DateField(auto_now_add=True, null=True, blank=True, help_text="确认日期",
                                  verbose_name="确认日期")
    verifyPerson = models.CharField(max_length=16, blank=True, null=True, verbose_name="验证人员", help_text="验证人员")
    verifyDate = models.DateField(auto_now_add=True, null=True, blank=True, help_text="验证日期",
                                  verbose_name="验证日期")
    project = models.ForeignKey(to="Project", db_constraint=False, related_name="projField", on_delete=models.CASCADE,
                                verbose_name='归属项目', help_text='归属项目', related_query_name='projQuery')
    case = models.ManyToManyField(to="Case", db_constraint=False, related_name="caseField", verbose_name='归属测试用例',
                                  help_text='归属测试用例-多对多', related_query_name='caseQuery')
    solve = models.TextField(verbose_name='开发人员填写-改正措施',
                             help_text='开发人员填写-改正措施，该字段需要关联“status=1”', blank=True, null=True)
    analysis = HTMLField(blank=True, null=True, verbose_name="开发人员填写-原因分析", help_text="开发人员填写-原因分析")
    effect_scope = HTMLField(blank=True, null=True, verbose_name="开发人员填写-影响域分析",
                             help_text="开发人员填写-影响域分析")
    verify_result = HTMLField(blank=True, null=True, verbose_name="回归结果", help_text="回归结果")

    def __str__(self):
        return f'问题单:{self.ident}-{self.name}'

    class Meta:
        db_table = 'project_problem'
        verbose_name = "问题单"
        verbose_name_plural = verbose_name
        ordering = ('id',)

# 单位信息
class Contact(CoreModel):
    objects = models.Manager()
    entrust_person = models.CharField(max_length=16, blank=True, verbose_name="法人", help_text="法人")
    name = models.CharField(max_length=64, blank=True, verbose_name="公司名称", help_text="公司名称")
    key = models.IntegerField(auto_created=True, verbose_name="公司编号", help_text="公司编号")
    # 新增地址
    addr = models.CharField(max_length=64, blank=True, verbose_name="公司地址", help_text="公司地址")
    # 新增简称
    refer_name = models.CharField(max_length=32, blank=True, verbose_name='公司简称', help_text='公司简称')

    def __str__(self):
        return f'联系方式:{self.name}'

    class Meta:
        db_table = 'contact_gongsi'
        verbose_name = '委托方、研制方、测试方信息'
        verbose_name_plural = verbose_name
        ordering = ('create_datetime',)

# ~~~~~2024年2月27日新增~~~~~
class Abbreviation(models.Model):
    objects = models.Manager()
    title = models.CharField(max_length=64, verbose_name="缩略语", help_text="缩略语")
    des = models.CharField(max_length=256, verbose_name="描述", help_text="描述")

    def __str__(self):
        return f'缩略语:{self.title}'

    class Meta:
        db_table = 'project_abbreviation'
        verbose_name = '缩略语和行业词汇'
        verbose_name_plural = '缩略语和行业词汇'
