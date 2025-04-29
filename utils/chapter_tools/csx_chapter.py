from apps.project.models import Round
from utils.util import get_dict_info

def create_csx_chapter_dict(one_round: Round):
    """传入轮次对象，返回测试项类型字典key的数组/测试项key的dict，以便后续使用"""
    testType_list = []
    last_chapter_items = {}
    if one_round:
        for csx in one_round.rtField.all():
            if csx.testType not in testType_list:
                testType_list.append(csx.testType)
        # 排序需要查字典里面index来排序
        testType_list.sort(key=lambda x: get_dict_info('testType', x)['index'], reverse=False)
        for test_type in testType_list:
            last_chapter_items[test_type] = []
        for csx in one_round.rtField.all():
            last_chapter_items[csx.testType].append(csx.key)
    return testType_list, last_chapter_items
