# ~~~~确定响应codes的枚举类型~~~~
# 1.账号账户和密码错误的code -> status:部分401
HTTP_USER_PASSWORD_ERROR_CODE: int = 40001
# 2.传给后端的数据越界
HTTP_INDEX_ERROR: int = 40038
# 3.当右键测试项时，如果测试项下面已经有用例了
HTTP_EXISTS_CASES:int = 40031
# 4.特权账号登录需要图形验证码：业务码下发前端按需显示验证码输入框（登录页默认不显示，
#   普通用户零影响；不设探测接口，避免特权账号名单可被枚举）
HTTP_CAPTCHA_REQUIRED: int = 40002


# ~~~~下面是HttpError的status_code对应的错误信息~~~~
# 1.项目看板-项目结束时间早于最后一个轮次结束时间
PROJECT_ENDTIME_ERROR_CODE: int = 500412
