from apps.project.models import Project
from utils.chapter_tools.csx_chapter import create_csx_chapter_dict
from utils.util import get_testType, get_case_ident

# 传入项目对象、dut的类型例如'XQ'、round_str字符串表示例如第一轮为'XQ'，测试项其实章节前缀例如
def create_bg_round1_zhui(project_obj: Project, dut_str='XQ', round_str='0'):
    """传入项目对象，返回{仅第一轮}的design_list渲染到模版的列表"""
    # 首先定义后面用问题单前缀
    problem_prefix = "".join(['PT_', project_obj.ident, '_'])
    # 如果是第一轮，测试项章节号前缀则为6.2，其他轮次为4.1
    demand_prefix = '6.2' if round_str == '0' else "3.1"
    design_list = []
    round_obj = project_obj.pField.filter(key=round_str).first()  # 轮次对象
    case_index = 1
    if round_obj:
        testType_list, last_chapter_items = create_csx_chapter_dict(round_obj)
        specific_dut = round_obj.rdField.filter(type=dut_str).first()  # design的列表
        if dut_str == 'XQ':
            so_dut = round_obj.rdField.filter(type='SO').first()
            if so_dut:
                designs = so_dut.rsField.all()
                for design in designs:
                    design_dict = {'name': "/", 'chapter': "/", 'test_demand': []}
                    # 获取一个design的所以测试项，包括关联测试项
                    test_items = []
                    test_items.extend(design.dtField.all())
                    test_items.extend(design.odField.all())
                    for test_item in test_items:
                        key_index = int(test_item.key.split("-")[-1]) + 1
                        test_index = str(key_index).rjust(3, '0')
                        reveal_ident = "_".join(
                            ["XQ", get_testType(test_item.testType, "testType"),
                             test_item.ident, test_index])
                        test_item_last_chapter = last_chapter_items[test_item.testType].index(test_item.key) + 1
                        test_chapter = ".".join([demand_prefix, str(testType_list.index(test_item.testType) + 1),
                                                 str(test_item_last_chapter)])
                        test_item_dict = {'name': test_item.name, 'chapter': test_chapter, 'ident': reveal_ident,
                                          'case_list': []}
                        for case in test_item.tcField.all():
                            # 用例如果关联了问题单，那么直接判断未通过，如果没有关联问题单，则找步骤里面是否有未执行
                            # 如果未执行，不显示未执行，显示“/”斜杠
                            is_passed = '通过'
                            problem_ident_list = []
                            for problem in case.caseField.all():
                                problem_ident_list.append("".join([problem_prefix, problem.ident]))
                            if len(problem_ident_list) > 0:
                                is_passed = '未通过'
                            case_dict = {
                                'index': case_index,
                                'name': case.name,
                                'ident': get_case_ident(reveal_ident, case),
                                'passed': is_passed,
                                'problem_ident_list': "\a".join(problem_ident_list)
                            }
                            test_item_dict['case_list'].append(case_dict)
                            case_index += 1
                        design_dict['test_demand'].append(test_item_dict)
                    design_list.append(design_dict)

        if specific_dut:
            designs = specific_dut.rsField.all()
            for design in designs:
                design_dict = {'name': design.name, 'chapter': design.chapter, 'test_demand': []}
                # 获取一个design的所以测试项，包括关联测试项
                test_items = []
                test_items.extend(design.dtField.all())
                test_items.extend(design.odField.all())
                for test_item in test_items:
                    key_index = int(test_item.key.split("-")[-1]) + 1
                    test_index = str(key_index).rjust(3, '0')
                    reveal_ident = "_".join(
                        ["XQ", get_testType(test_item.testType, "testType"),
                         test_item.ident, test_index])
                    test_item_last_chapter = last_chapter_items[test_item.testType].index(test_item.key) + 1
                    test_chapter = ".".join([demand_prefix, str(testType_list.index(test_item.testType) + 1),
                                             str(test_item_last_chapter)])
                    test_item_dict = {'name': test_item.name, 'chapter': test_chapter, 'ident': reveal_ident,
                                      'case_list': []}
                    for case in test_item.tcField.all():
                        # 用例如果关联了问题单，那么直接判断未通过，如果没有关联问题单，则找步骤里面是否有未执行
                        # 如果未执行，不显示未执行，显示“/”斜杠
                        is_passed = '通过'
                        problem_ident_list = []
                        for problem in case.caseField.all():
                            problem_ident_list.append("".join([problem_prefix, problem.ident]))
                        if len(problem_ident_list) > 0:
                            is_passed = '未通过'
                        case_dict = {
                            "index": case_index,
                            'name': case.name,
                            'ident': get_case_ident(reveal_ident, case),
                            'passed': is_passed,
                            'problem_ident_list': "\a".join(problem_ident_list)
                        }
                        test_item_dict['case_list'].append(case_dict)
                        case_index += 1
                    design_dict['test_demand'].append(test_item_dict)
                design_list.append(design_dict)
    return design_list
