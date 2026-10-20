"""文档生成辅助函数的单元测试（纯函数，不依赖数据库）。"""
from django.test import SimpleTestCase

from utils.chapter_tools.csx_chapter import chapter_no
from utils.util import digit_to_chinese


class DigitToChineseTests(SimpleTestCase):
    def test_first_ten(self):
        self.assertEqual(digit_to_chinese(1), '一')
        self.assertEqual(digit_to_chinese(10), '十')

    def test_more_than_ten(self):
        # 轮次 ≥10 是原固定列表版本会 IndexError 的场景
        self.assertEqual(digit_to_chinese(11), '十一')
        self.assertEqual(digit_to_chinese(20), '二十')
        self.assertEqual(digit_to_chinese(21), '二十一')
        self.assertEqual(digit_to_chinese(101), '一百零一')

    def test_invalid_value(self):
        self.assertEqual(digit_to_chinese(None), 'None')
        self.assertEqual(digit_to_chinese('abc'), 'abc')


class ChapterNoTests(SimpleTestCase):
    def test_exists(self):
        self.assertEqual(chapter_no(['4', '2'], {'4': ['0', '1'], '2': ['0']}, '4', '1'), (1, 2))
        self.assertEqual(chapter_no(['4', '2'], {'4': ['0', '1'], '2': ['0']}, '2', '0'), (2, 1))

    def test_missing_type_or_item(self):
        # 关联测试项属于其他轮次时不应抛 ValueError
        self.assertIsNone(chapter_no(['4'], {'4': ['0']}, '2', '0'))
        self.assertIsNone(chapter_no(['4'], {'4': ['0']}, '4', '9'))
        self.assertIsNone(chapter_no([], {}, '4', '0'))
