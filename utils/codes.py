# 确定响应codes的枚举类型
# 1.账号账户和密码错误的code -> status:部分401
HTTP_USER_PASSWORD_ERROR_CODE: int = 40001
# 2.传给后端的数据越界
HTTP_INDEX_ERROR: int = 40038
# 3.当右键测试项时，如果测试项下面已经有用例了
HTTP_EXISTS_CASES:int = 40031
