# 该类主要传入文档片段列表，对列表进行数据组装等工作
from django.db.models import QuerySet
# Models
from apps.dict.models import Fragment

class FragmentOperation(object):
    def __init__(self, fragments: QuerySet[Fragment] = None):
        self.__fragments = fragments  # 初始化必须：传入Fragment-Model对象

    @property
    def fragment(self):
        return self.__fragments
