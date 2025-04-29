from enum import Enum, unique

# 产品文档名称
@unique
class DocNameEnum(Enum):
    dg = 1
    sm = 2
    jl = 3
    hsm = 4
    hjl = 5
    bg = 6
    wtd = 7

if __name__ == '__main__':
    print(DocNameEnum.dg)
    print(DocNameEnum.dg.value)
