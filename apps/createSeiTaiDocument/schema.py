"""定义生成最终文档的BaseModel"""
from typing import List
from ninja import Schema

# 定义文档片段输入的Schema，用于输入Schema嵌套
class FragmentItemInputSchema(Schema):
    name: str
    isCover: bool = True  # 默认为需要覆盖生成文档

# 输入Schema
class SeitaiInputSchema(Schema):
    id: int
    frag: List[FragmentItemInputSchema]
