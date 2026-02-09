"""该模块主要自动生成静态分析、代码审查以及文档审查的设计需求、测试项、用例"""
from apps.project.models import (
    Project,
    Dut,
    Design,
    TestDemand,
    TestDemandContent,
    TestDemandContentStep,
    Case,
    CaseStep
)

# 导入人机交互界面固定数据
from apps.project.tools.rj_data_cont import rj_data

def auto_create_jt_and_dm(user_name: str, dut_qs: Dut, project_obj: Project):
    """传入源代码dut以及测试人员名称username，自动在dut下面生成静态分析和代码审查设计需求、测试项、用例"""
    # 先查询dut_qs下面有多少design，以便写里面的key
    design_index = dut_qs.rsField.count()
    # 1.1.自动创建design静态分析
    jt_design_create_dict = {
        'ident': 'JTFX',
        'name': '静态分析',
        'demandType': '6',
        'description': "依据相关的要求，利用静态分析工具对被测软件全部源程序进行控制流分析、"
                       "数据流分析进行分析，并统计软件质量度量信息，给出软件源代码检查结果",
        'title': '静态分析',
        'key': ''.join([dut_qs.key, '-', str(design_index)]),
        'level': '2',
        'chapter': '/',
        'project': project_obj,
        'round': dut_qs.round,
        'dut': dut_qs
    }
    design_index += 1
    new_design_jt: Design = Design.objects.create(**jt_design_create_dict)
    # 1.1.1.自动创建demand静态分析
    jt_demand_create_dict = {
        'ident': 'JTFX',
        'name': '静态分析',
        'adequacy': '1）对软件全部源代码进行静态分析；\a'
                    '2）对度量指标不满足指标要求的模块，应进行专项代码审查；\a'
                    '3）按照控制流和数据流分析表单，对软件的控制流和数据流进行分析。',
        'priority': '2',
        'testType': '15',
        'testMethod': ["3"],
        'testDesciption': '对被测软件全部源程序进行静态分析，'
                          '对控制流、数据流进行分析，验证软件是否满足控制流和数据流要求，'
                          '并依据质量特性需求统计质量度量信息',
        'title': '静态分析',
        'key': ''.join([new_design_jt.key, '-', '0']),
        'level': '3',
        'project': project_obj,
        'round': new_design_jt.round,
        'dut': new_design_jt.dut,
        'design': new_design_jt,
    }
    new_demand_jt = TestDemand.objects.create(**jt_demand_create_dict)
    new_demand_content_obj = TestDemandContent.objects.create(testDemand=new_demand_jt, subName='静态分析')
    TestDemandContentStep.objects.create(testDemandContent=new_demand_content_obj,
                                         operation='根据静态分析的审查项和技术要求以及被测软件质量特性需求，'
                                                   '编制检查单。使用静态分析工具Testbed和klocwork进行静态分析，对程序进行检查：\a'
                                                   '1）使用静态分析工具统计软件质量度量信息；\a'
                                                   '2）使用静态分析工具对软件进行规则检查；\a'
                                                   '3）使用静态分析工具结合人工分析对控制流和数据流进行分析。')
    new_case_jt = Case.objects.create(
        ident='JTFX',
        name='静态分析',
        initialization='已获取全部被测件源代码程序，静态分析工具准备齐备',
        premise='提交的代码出自委托方受控库，是委托方正式签署外发的',
        summarize='依据委托方的要求进行静态分析，验证软件质量度量和编码规则是否满足军标要求',
        designPerson=user_name,
        testPerson=user_name,
        monitorPerson=user_name,
        project=project_obj,
        isLeaf=True,
        round=new_demand_jt.round,
        dut=new_demand_jt.dut,
        design=new_demand_jt.design,
        test=new_demand_jt,
        title='静态分析',
        key=''.join([new_demand_jt.key, '-', '0']),
        level='4'
    )
    CaseStep.objects.create(case=new_case_jt,
                            operation='使用LDRA TestBed软件和Klocwork软件工具对被测软件'
                                      '全部源程序进行静态分析，并配合人工以及检查单进行分析',
                            expect='静态审查单全部通过，且源代码满足编码规则和质量度量要求',
                            result='静态度量结果符合国军标要求，静态分析审查单全部通过', )
    # 1.2.自动创建代码审查design
    dm_design_create_dict = {
        'ident': 'DMSC',
        'name': '代码审查',
        'demandType': '6',
        'description': "依据相关要求及软件文档开展针对软件程序代码的代码审查",
        'title': '代码审查',
        'key': ''.join([dut_qs.key, '-', str(design_index)]),
        'level': '2',
        'chapter': '/',
        'project': dut_qs.project,
        'round': dut_qs.round,
        'dut': dut_qs
    }
    new_design_dm = Design.objects.create(**dm_design_create_dict)
    dm_demand_create_dict = {
        'ident': 'DMSC',
        'name': '代码审查',
        'adequacy': '根据代码审查单的审查项，工具审查完成全部代码的审查，人工审查完成关键模块的审查，'
                    '审查中发现的问题均得到有效处理。',
        'priority': '2',
        'testType': '2',
        'testMethod': ["3"],
        'title': '代码审查',
        'testDesciption': '通过人工审查及借助klocwork、Testbed工具辅助分析的方式开展代码审查，'
                          '审查代码和设计的一致性、代码执行标准的情况、代码逻辑表达的正确性、'
                          '代码结构的合理性以及代码的可读性。人工审查中发现的问题，审查人员应及时记录。',
        'key': ''.join([new_design_dm.key, '-', '0']),
        'level': '3',
        'project': project_obj,
        'round': new_design_dm.round,
        'dut': new_design_dm.dut,
        'design': new_design_dm,
    }
    new_demand_dm = TestDemand.objects.create(**dm_demand_create_dict)
    new_content_obj = TestDemandContent.objects.create(
        testDemand=new_demand_dm,
        subName='代码审查'
    )
    TestDemandContentStep.objects.create(
        testDemandContent=new_content_obj,
        operation='使用klocwork、testbed工具根据本大纲附录B中的代码审查单对代码审查范围内的源代码开展四个方面的审查，'
                  '人工对所选模块进行如下四个方面的审查：\a'
                  '1）编程准则检查：依据编程准则的要求，对程序的编码与编程准则进行符合性检查；\a'
                  '2）代码流程审查：审查程序代码的条件判别、控制流程、数据处理等满足设计要求；\a'
                  '3）软件结构审查：依据设计文档，审查程序代码的结构设计的合理性，包括程序结构设计和数据结构设计；\a'
                  '4）需求实现审查：依据需求文档及其他相关资料，审查程序代码的需求层的功能实现是否正确。',
    )
    new_case_dm = Case.objects.create(
        ident='DMSC',
        name='代码审查',
        initialization='代码已提交',
        premise='提交的代码出自委托方受控库，是委托方正式签署外发的',
        summarize='通过人工审查及借助工具辅助分析的方式开展代码审查，审查代码编程准则的符合性、'
                  '代码流程实现的正确性、代码结构的合理性以及代码实现需求的正确性；人工审查中发现的问题，审查人员应及时记录',
        designPerson=user_name,
        testPerson=user_name,
        monitorPerson=user_name,
        project=project_obj,
        isLeaf=True,
        round=new_demand_dm.round,
        dut=new_demand_dm.dut,
        design=new_demand_dm.design,
        test=new_demand_dm,
        title='代码审查',
        key=''.join([new_demand_dm.key, '-', '0']),
        level='4'
    )
    CaseStep.objects.create(case=new_case_dm,
                            operation='通过人工审查及借助工具辅助分析的方式开展代码审查，审查代码编程准则的符合性、'
                                      '代码流程实现的正确性、代码结构的合理性以及代码实现需求的正确性；'
                                      '人工审查中发现的问题，审查人员应及时记录',
                            expect='代码设计正确，满足审查单要求，无不符合项',
                            result='代码设计正确，满足审查单要求，无不符合项', )

def auto_create_wd(user_name: str, dut_qs: Dut, project_obj: Project):
    """传入用户名、在dut下创建、项目对象，自动创建文档审查的设计需求、测试项、测试用例"""
    # 先查询dut_qs下有多少desgin，然后设置key
    design_index = dut_qs.rsField.count()
    # 1.1.自动创建文档审查design
    wd_design_create_dict = {
        'ident': 'WDSC',
        'name': '文档审查',
        'demandType': '6',
        'description': "依据相关要求，逐项检查被测文档的齐套性、完整性、一致性和准确性是否满足要求",
        'title': '文档审查',
        'key': ''.join([dut_qs.key, '-', str(design_index)]),
        'level': '2',
        'chapter': '/',
        'project': project_obj,
        'round': dut_qs.round,
        'dut': dut_qs
    }
    new_wd_design_obj: Design = Design.objects.create(**wd_design_create_dict)
    # 1.1.1.自动创建demand文档审查
    is_JD = (project_obj.report_type == '9')
    test_des = "本次三方文档审查内容包括软件需求规格说明、软件设计说明等"
    wd_demand_create_dict = {
        'ident': 'WDSC',
        'name': '文档审查',
        'adequacy': '按照审查单审查文档的齐套性、完整性、一致性、准确性。',
        'priority': '1',
        'testType': '8',
        'testMethod': ["3"],
        'title': '文档审查',
        'testDesciption': '本次文档审查包括的内容如下：\a'
                          '1）软件需求规格说明\a'
                          '2）软件详细设计说明\a'
                          '3）软件开发计划\a'
                          '4）软件配置管理计划\a'
                          '5）软件质量保证计划\a'
                          '6）软件单元测试计划\a'
                          '7）软件单元测试说明\a'
                          '8）软件单元测试报告\a'
                          '9）配置项测试计划\a'
                          '10）配置项测试说明\a'
                          '11）配置项测试报告\a'
                          '12）软件用户手册\a'
                          '13）软件研制总结报告\a'
                          '14）软件版本说明\a'
                          '15）软件产品规格说明\a'
                          '16）固件保障手册' if is_JD else test_des,
        'key': ''.join([new_wd_design_obj.key, '-', '0']),
        'level': '3',
        'project': project_obj,
        'round': new_wd_design_obj.round,
        'dut': new_wd_design_obj.dut,
        'design': new_wd_design_obj,
    }
    new_wd_demand_obj = TestDemand.objects.create(**wd_demand_create_dict)
    new_wd_content_obj = TestDemandContent.objects.create(testDemand=new_wd_demand_obj, subName='文档审查')
    TestDemandContentStep.objects.create(
        testDemandContent=new_wd_content_obj,
        operation='根据文档审查表人工逐项检查，检查此项目文档的齐套性、完整性、规范性：\a'
                  '1）使用人工审查方法，按照附录A中文档齐套性审查单检查需求类、设计类、用户类、测试类文档是否齐套；\a'
                  '2）使用人工审查方法，按照附录A中需求规格说明审查单对软件需求规格说明逐项检查；\a'
                  '3）使用人工审查方法，按照附录A中软件设计文档审查单逐项检查。',
        expect='被测软件文档种类齐全，内容完整，描述准确，格式规范；\a'
               '2）需求文档内容完整，描述准确，格式规范，文档文文一致、文实相符；\a'
               '3）设计说明文档内容完整，描述准确，格式规范，文档文文一致、文实相符。',
    )
    new_wd_case_obj = Case.objects.create(
        ident='WDSC',
        name='文档审查',
        initialization='开发方已提交被测文档',
        premise='提交的文档出自委托方受控库，是委托方正式签署外发的',
        summarize='测试人员阅读文档，依据文档检查单对软件文档进行审查，审查文档内容是否完整、'
                  '文档描述是否准确、文档格式是否规范、文档是否文文一致',
        designPerson=user_name,
        testPerson=user_name,
        monitorPerson=user_name,
        project=project_obj,
        isLeaf=True,
        round=new_wd_demand_obj.round,
        dut=new_wd_demand_obj.dut,
        design=new_wd_demand_obj.design,
        test=new_wd_demand_obj,
        title='文档审查',
        key=''.join([new_wd_demand_obj.key, '-', '0']),
        level='4'
    )
    CaseStep.objects.create(case=new_wd_case_obj,
                            operation='按照测试需求中文档齐套性检查单检查需求类、设计类、用户类、测试类文档是否齐套',
                            expect='文档齐套性检查单全部通过，软件文档齐套',
                            result='文档齐套性检查单全部通过，软件文档齐套', )
    CaseStep.objects.create(case=new_wd_case_obj,
                            operation='按照测试需求中文档需求规格说明、设计文档等审查单，对相关文档进行审查',
                            expect='文档满足完整性、准确性、规范性和一致性的要求',
                            result='文档检查单全部审查通过，文档内容完整、文档描述准确、'
                                   '文档格式规范、文档文文一致', )

def auto_create_renji(user_name: str, dut_qs: Dut, project_obj: Project):
    """传入用户名、在dut下创建、项目对象，自动创建人机交互界面的设计需求、测试项、测试用例"""
    # 先查询dut_qs下有多少desgin，用于设置key
    design_index = dut_qs.rsField.count()
    for item in rj_data:
        # 创建设计需求
        rj_design_create_dict = {
            'ident': item['ident'],
            'name': item['desgin_name'],
            'demandType': '6',
            'description': item['xq_desc'],
            'title': item['desgin_name'],
            'key': ''.join([dut_qs.key, '-', str(design_index)]),
            'level': '2',
            'chapter': '/',
            'project': project_obj,
            'round': dut_qs.round,
            'dut': dut_qs
        }
        design_index += 1
        new_design_rj: Design = Design.objects.create(**rj_design_create_dict)
        # 创建测试项
        rj_demand_create_dict = {
            'ident': item['ident'],
            'name': item['test_item_name'],
            'adequacy': item['chongfen'],
            'priority': '2',
            'testType': '12',
            'testMethod': ["4"],
            'testDesciption': '在界面进行观察与操作，对照需求规格说明的功能需求进行比对，对照用户手册进行比对',
            'title': item['test_item_name'],
            'key': ''.join([new_design_rj.key, '-', '0']),
            'level': '3',
            'project': project_obj,
            'round': new_design_rj.round,
            'dut': new_design_rj.dut,
            'design': new_design_rj,
        }
        new_demand_rj = TestDemand.objects.create(**rj_demand_create_dict)
        new_demand_content_obj = TestDemandContent.objects.create(testDemand=new_demand_rj,
                                                                  subName=item['test_item_name'])
        for operation in item['test_method']:
            TestDemandContentStep.objects.create(testDemandContent=new_demand_content_obj,
                                                 operation=operation['caozuo']
                                                 , expect=operation['yuqi'])
        # 创建测试用例
        new_case_rj = Case.objects.create(
            ident=item['ident'],
            name=item['test_item_name'],
            initialization='已获取被测件的用户手册',
            premise='软件可正常运行，界面初始化完成',
            summarize=item['xq_desc'],
            designPerson=user_name,
            testPerson=user_name,
            monitorPerson=user_name,
            project=project_obj,
            isLeaf=True,
            round=new_demand_rj.round,
            dut=new_demand_rj.dut,
            design=new_demand_rj.design,
            test=new_demand_rj,
            title=item['test_item_name'],
            key=''.join([new_demand_rj.key, '-', '0']),
            level='4'
        )
        for operation in item['test_method']:
            CaseStep.objects.create(case=new_case_rj,
                                    operation=operation['caozuo'],
                                    expect=operation['yuqi'],
                                    result='界面操作结果符合预期', )
