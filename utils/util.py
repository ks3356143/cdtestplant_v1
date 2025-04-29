from typing import List
from apps.dict.models import DictItem
from apps.project.models import TestDemand
from html.parser import HTMLParser
from django.db.models import QuerySet
# 导入生成文档检查器log - 单例模式
from apps.createSeiTaiDocument.extensions.logger import GenerateLogger

logger = GenerateLogger(model='字典模块')

# 传入一个字符串数字以及字典标志code，返回真实的title名字
def get_str_dict(a, dict_code):
    dict_obj = DictItem.objects.filter(dict__code=dict_code, key=a).first()
    if dict_obj:
        return dict_obj.title
    else:
        # 如果用户没填写内容则记录检查中心log
        logger.write_warning_log(fragment='字典数据缺失', message=f'字典数据{dict_code}数据缺失，请检查相应数据是否存在')
        return ''

# 传入一个字符串数字以及字典标志code，返回字典所属的缩写(show_title)
def get_str_abbr(a, dict_code):
    dict_obj = DictItem.objects.filter(dict__code=dict_code, key=a).first()
    if dict_obj:
        return dict_obj.show_title
    else:
        logger.write_warning_log(fragment='字典数据缺失',
                                 message=f'查询字段数据缩写问题，字典数据{dict_code}数据可能缺失')
        return ""

# 传入一个字符串数组（测试项类型），字典标志code，返回(真实title,sort)
def get_str_dict_plus(a, dict_code):
    dict_obj = DictItem.objects.filter(dict__code=dict_code, key=a).first()
    if dict_obj:
        return dict_obj.title, dict_obj.sort
    else:
        logger.write_warning_log(fragment='字典数据查询错误', message=f'字典{dict_code}未查询到数据，请检查')
        return "", 1

# 找到testType字典中的缩写，例如“DC”“FT”
def get_testType(a, dict_code):
    dict_obj = DictItem.objects.filter(dict__code=dict_code, key=a).first()
    if dict_obj:
        return dict_obj.show_title
    else:
        logger.write_warning_log(fragment='字典数据查询错误',
                                 message=f'查询字段数据缩写问题，字典数据{dict_code}数据可能缺失')
        return ""

# 标识处理：获取测试需求（测试项的）生成文档的ident（标识）
def get_ident(test_item):
    # key_index = int(test_item.key.split("-")[-1]) + 1
    # test_index = str(key_index).rjust(3, '0')
    reveal_ident = "_".join(
        ["XQ", get_testType(test_item.testType, "testType"), test_item.ident])
    return reveal_ident

# 标识处理：传入demand的ident以及case，返回case的ident
def get_case_ident(demand_ident, case):
    key_index = int(case.key.split("-")[-1]) + 1
    test_index = str(key_index).rjust(3, '0')
    reveal_ident = "_".join([demand_ident.replace("XQ", "YL"), test_index])
    return reveal_ident

# 传入字典code，以及字符串数组返回一个数组，每个数组是dict
def get_list_dict(dict_code: str, str_list: List[str]):
    result = []
    qss = DictItem.objects.filter(dict__code=dict_code)
    for st in str_list:
        res = {}
        for qs in qss:
            if st == qs.key:
                res['ident_version'] = qs.title
                res['doc_name'] = qs.doc_name
                res['publish_date'] = qs.publish_date
                res['source'] = qs.source
                result.append(res)
    return result

# 传入字典code，以及字符串数组返回一个列表，每个元素是dict，包含字典item很多信息
def get_list_dict_info(dict_code, str_list):
    """传入字典的字符串列表，输出每个元素为dict的列表信息"""
    result = []
    qss = DictItem.objects.filter(dict__code=dict_code)  # type:ignore
    for st in str_list:
        res = {}
        for qs in qss:
            if st == qs.key:
                res['title'] = qs.title
                res['index'] = qs.sort
                result.append(res)
    return result

# 传入字典code，以及单个字典字符串，输出一个dict带信息
def get_dict_info(dict_code, item_str):
    """传入字典的字符串单个表示，输出dict包含排序index字段"""
    qss = DictItem.objects.filter(dict__code=dict_code)
    res = {}
    for qs in qss:
        if item_str == qs.key:
            res['title'] = qs.title
            res['index'] = qs.sort
    return res

# 简单HTML解析器 - 解析富文本的parser - 复杂的使用apps/createDocument/extensions/parse_rich_text.py
class MyHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.allStrList = []

    def error(self, message):
        print("HTML解析器出错，error信息为：", message)

    def handle_starttag(self, tag, attrs):
        if tag == 'img':
            img_base64 = attrs[0][1]
            self.allStrList.append(img_base64)

    def handle_endtag(self, tag):
        pass

    def handle_data(self, data):
        if data != '\n':
            self.allStrList.append(data)

# 不提取图片的HTML解析器
class MyHTMLParser_p(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.allStrList = []

    def handle_data(self, data):
        if data != '\n':
            self.allStrList.append(data)

def create_problem_grade_str(problems):
    """传入问题qs，生成到文档的字符串：严重问题4个、一般问题10个"""
    problem_r1_grade_dict = {}
    for problem in problems:
        grade_key: str = get_str_dict(problem.grade, 'problemGrade')
        if grade_key in problem_r1_grade_dict.keys():
            problem_r1_grade_dict[grade_key] += 1
        else:
            problem_r1_grade_dict[grade_key] = 1
    problem_r1_grade_list = []
    for key, value in problem_r1_grade_dict.items():
        problem_r1_grade_list.append("".join([f"{key}问题", f"{value}个"]))
    return "、".join(problem_r1_grade_list)

def create_problem_type_str(problems):
    """传入问题qs，生成到文档的字符串：文档问题1个，程序问题10个"""
    problem_r1_type_dict = {}
    for problem in problems:
        type_key: str = get_str_dict(problem.type, 'problemType')
        if type_key in problem_r1_type_dict.keys():
            problem_r1_type_dict[type_key] += 1
        else:
            problem_r1_type_dict[type_key] = 1
    problem_r1_type_list = []
    for key, value in problem_r1_type_dict.items():
        problem_r1_type_list.append("".join([f"{key}", f"{value}个"]))
    return "、".join(problem_r1_type_list)

def create_str_testType_list(cases):
    """传入用例的qs，生成其测试类型的字符串：例如包含xxx测试5个，xxx测试11个，返回的是元组第二个元素表示测试类型个数"""
    test_type_set: set = set()
    for case in cases:
        demand: TestDemand = case.test
        test_type_set.add(demand.testType)
    test_type_list = get_list_dict_info('testType', list(test_type_set))
    test_type_list.sort(key=lambda x: int(x['index']))
    round1_testType_list = list(map(lambda x: x['title'], test_type_list))
    return round1_testType_list, len(test_type_list)

def util_func(item):
    """辅助函数，将下面函数返回的summary_list改造为以需求类型执行统计列表"""
    transform_item = {'title': item['title'], 'total_count': 0, 'exe_count': 0, 'not_exe_count': 0, 'pass_count': 0,
                      'not_pass_count': 0}
    for it in item['demand_list']:
        transform_item['total_count'] += it['total_count']
        transform_item['exe_count'] += it['exe_count']
        transform_item['not_exe_count'] += it['not_exe_count']
        transform_item['pass_count'] += it['pass_count']
        transform_item['not_pass_count'] += it['not_pass_count']
    return transform_item

def create_demand_summary(demands: QuerySet, project_ident: str):
    """
        [
            {
                'title':'功能测试_5',
                'demand_list':[
                    {
                        'name': '测试项1',
                        'total_count': 1,
                        'exe_count': 1,
                        'not_exe_count': 0,
                        'pass_count': 1,
                        'not_pass_count': 0,
                        'conclusion': '通过',
                        'problems': '/'
                    }
                ]
            },
        ]
    """
    summary_dict = {}  # 后面再变为数组
    # 1.首先根据testType字段生成一个一个dict
    for demand in demands:
        # 取出testType -> '4'（后面查字典）
        test_type_num = demand.testType
        # 查出需求类型的sort与testType真实名字,组合为一个字符串作为key
        testTypeStr, testTypeSort = get_str_dict_plus(test_type_num, 'testType')
        testType_info = testTypeStr + '_' + str(testTypeSort)
        demand_dict = {
            'name': demand.name,
            'total_count': 0,
            'exe_count': 0,
            'not_exe_count': 0,
            'pass_count': 0,
            'not_pass_count': 0,
            'conclusion': '通过',
            'problems': "/"
        }
        # 查询当前测试需求下用例
        demand_problem_list = set()
        for case in demand.tcField.all():
            demand_dict['total_count'] += 1
            # 要遍历下面的测试步骤
            isPassed = True
            isExe = True
            for step in case.step.all():
                # 所有步骤有一个未通过则是未通过，所有都执行则是已执行
                if step.passed == '2':
                    isPassed = False
                    isExe = True
                    break
                if step.passed == '3':
                    isExe = False
            if isPassed:
                demand_dict['pass_count'] += 1
            else:
                demand_dict['not_pass_count'] += 1
                demand_dict['conclusion'] = '未通过'
            if isExe:
                demand_dict['exe_count'] += 1
            else:
                demand_dict['not_exe_count'] += 1
            # 查询每个用例下面的问题单，将问题单的ident弄出来
            for problem in case.caseField.all():
                problem_ident = 'PT_' + project_ident + '_' + problem.ident.rjust(3, '0')
                demand_problem_list.add(problem_ident)
        if len(list(demand_problem_list)) > 0:
            demand_dict['problems'] = "\a".join(list(demand_problem_list))
        if testType_info in summary_dict.keys():
            summary_dict[testType_info].append(demand_dict)
        else:
            summary_dict[testType_info] = [demand_dict]
    summary_list = []
    for key, value in summary_dict.items():
        one_dict = {
            'title': key,
            'demand_list': value
        }
        summary_list.append(one_dict)
    # 根据其排序
    summary_list.sort(key=lambda x: int(x['title'].split('_')[-1]))
    # 然后将_5这种替换掉
    for one in summary_list:
        one['title'] = one['title'].split("_")[0]
    # ~~~~还需要返回一个 -> 测试类型的用例执行情况
    demandType_exe_list = list(map(util_func, summary_list))
    return summary_list, demandType_exe_list

def create_problem_table(problems):
    """传入问题单qs，输出按问题种类分的问题统计表的数据"""
    res_list = [{
        'name': '一般问题',
        'xq_count': 0,
        'sj_count': 0,
        'wd_count': 0,
        'bm_count': 0,
        'data_count': 0,
        'other_count': 0,
        'closed_count': 0,
        'non_closed_count': 0,
    }, {
        'name': '严重问题',
        'xq_count': 0,
        'sj_count': 0,
        'wd_count': 0,
        'bm_count': 0,
        'data_count': 0,
        'other_count': 0,
        'closed_count': 0,
        'non_closed_count': 0,
    }, {
        'name': '建议',
        'xq_count': 0,
        'sj_count': 0,
        'wd_count': 0,
        'bm_count': 0,
        'data_count': 0,
        'other_count': 0,
        'closed_count': 0,
        'non_closed_count': 0,
    }, {
        'name': '重大问题',
        'xq_count': 0,
        'sj_count': 0,
        'wd_count': 0,
        'bm_count': 0,
        'data_count': 0,
        'other_count': 0,
        'closed_count': 0,
        'non_closed_count': 0,
    }]

    for problem in problems:
        index = int(problem.grade) - 1
        if problem.type == '1':
            res_list[index]['other_count'] += 1
        elif problem.type == '2':
            res_list[index]['wd_count'] += 1
        elif problem.type == '3':
            res_list[index]['bm_count'] += 1
        elif problem.type == '4':
            res_list[index]['sj_count'] += 1
        elif problem.type == '5':
            res_list[index]['xq_count'] += 1
        elif problem.type == '6':
            res_list[index]['data_count'] += 1

        # 是否归零
        if problem.status == '1':
            res_list[index]['closed_count'] += 1
        else:
            res_list[index]['non_closed_count'] += 1
    return res_list

def create_problem_type_table(problems):
    """传入问题qs，解析出按测试类型分的问题统计表格"""
    res_list = [{
        'name': '一般问题',
        'wd_count': 0,
        'jt_count': 0,
        'dm_count': 0,
        'dt_count': 0,
        'data_count': 0,
        'closed_count': 0,
        'non_closed_count': 0,
    }, {
        'name': '严重问题',
        'wd_count': 0,
        'jt_count': 0,
        'dm_count': 0,
        'dt_count': 0,
        'data_count': 0,
        'closed_count': 0,
        'non_closed_count': 0,
    }, {
        'name': '建议',
        'wd_count': 0,
        'jt_count': 0,
        'dm_count': 0,
        'dt_count': 0,
        'data_count': 0,
        'closed_count': 0,
        'non_closed_count': 0,
    }, {
        'name': '重大问题',
        'wd_count': 0,
        'jt_count': 0,
        'dm_count': 0,
        'dt_count': 0,
        'data_count': 0,
        'closed_count': 0,
        'non_closed_count': 0,
    }]

    for problem in problems:
        index = int(problem.grade) - 1
        belong_demand: TestDemand = problem.case.all()[0].test
        if belong_demand.testType == '8':  # 属于文档审查问题
            res_list[index]['wd_count'] += 1
        elif belong_demand.testType == '15':  # 属于静态分析问题
            res_list[index]['jt_count'] += 1
        elif belong_demand.testType == '2' or belong_demand.testType == '3':  # 属于代码审查和走查
            res_list[index]['dm_count'] += 1
        else:  # 属于动态发现问题
            res_list[index]['dt_count'] += 1

        # 是否归零
        if problem.status == '1':
            res_list[index]['closed_count'] += 1
        else:
            res_list[index]['non_closed_count'] += 1
    return res_list

def get_demand_testTypes(demand_qs) -> str:
    """传入测试项qs，返回字符串类似于“静态分析、代码审查、功能测试等”"""
    testType_list = list(demand_qs.values("testType").distinct().order_by('testType'))
    t_code_list = [item['testType'] for item in testType_list]
    t_code_list = get_list_dict_info('testType', t_code_list)
    t_code_list.sort(key=lambda x: int(x['index']))
    t_str = [item['title'] for item in t_code_list]
    return '、'.join(t_str) if len(t_str) > 0 else "测试"
