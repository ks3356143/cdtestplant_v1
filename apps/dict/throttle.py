from ninja_extra.throttling import UserRateThrottle
# ~~~~~~~~~~~注意：当前只对缩略语添加1分钟一次，用于Jmeter测试，记得删除~~~~~~~~~~~
# 限流类 - 只能一分钟请求5次
class User60MinRateThrottle(UserRateThrottle):
    rate = '60/min'
    scope = 'minutes'
