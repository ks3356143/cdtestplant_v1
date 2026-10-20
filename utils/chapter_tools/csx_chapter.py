from apps.project.models import Round
from utils.util import get_dict_info


def chapter_no(testType_list, last_chapter_items, test_type, item_key):
    """返回 (测试类型序号, 项在类型内的序号)；数据不在本轮时返回 None。

    追踪表会同时遍历 design.odField（关联测试项），其中可能包含其他轮次的测试项；
    直接 list.index() 会 ValueError，这里统一做存在性判断。
    """
    items = last_chapter_items.get(test_type)
    if not items or test_type not in testType_list or item_key not in items:
        return None
    return testType_list.index(test_type) + 1, items.index(item_key) + 1


def create_csx_chapter_dict(one_round: Round):
    """传入轮次对象，返回测试项类型字典key的数组/测试项key的dict，以便后续使用"""
    testType_list = []
    last_chapter_items = {}
    if one_round:
        for csx in one_round.rtField.all():
            if csx.testType not in testType_list:
                testType_list.append(csx.testType)
        # 排序需要查字典里面index来排序；字典项缺失时排到最后，避免 KeyError
        testType_list.sort(key=lambda x: get_dict_info('testType', x).get('index', 10 ** 6), reverse=False)
        for test_type in testType_list:
            last_chapter_items[test_type] = []
        for csx in one_round.rtField.all():
            last_chapter_items[csx.testType].append(csx.key)
    return testType_list, last_chapter_items
