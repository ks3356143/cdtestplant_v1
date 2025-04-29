import jwt
from django.conf import settings
from threading import local
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils.functional import SimpleLazyObject
from django.contrib.auth import get_user_model
# 导入日志的模型
from apps.user.models import TableOperationLog, Users
# 导入其他模型用于排除
from apps.project.models import CaseStep, TestDemandContent
# 导入异常处理
from jwt.exceptions import ExpiredSignatureError
from utils.chen_response import ChenResponse
# 导入中间件记录日志模型
from apps.system.models import LoginLog
from apps.system.models import OperationLog

log_manager = TableOperationLog.objects

_thread_local = local()

def get_current_user():
    """
    获取当前用户对象，调用则从local对象里面获取user
    :return: Users实例
    """
    return getattr(_thread_local, 'user', None)

def clear_request_locals(sender, **kwargs):
    """
    被request_finished连接的信号处理函数，请求结束后清除local里面的user信息
    """
    _thread_local.user = None

def set_request_locals(sender, **kwargs):
    """
    被request_started连接的信号处理函数，_thread_local.user属性设置为当前登录用户
    """
    bearer_token = kwargs['environ'].get('HTTP_AUTHORIZATION', None)
    if not bearer_token or bearer_token == 'Bearer null':
        return
    bearer_token = bearer_token.replace('Bearer ', '')
    # 逻辑：先获取NINJA_JWT配置中秘钥、和加密算法信息
    jwt_settings = settings.NINJA_JWT
    jwt_secret = jwt_settings.get('SIGNING_KEY', None)
    jwt_algo = jwt_settings.get('ALGORITHM', None)
    # 如果为None，则使用settings中的秘钥和['HS256']算法
    secret_key = jwt_secret or settings.SECRET_KEY
    algorithms_str = jwt_algo or 'HS256'
    # 解决bug:因为过期前面不跳转首页处理方式
    try:
        jwt_dict = jwt.decode(bearer_token, secret_key, algorithms=[algorithms_str])
    except ExpiredSignatureError as exc:
        return ChenResponse(status=403, code=500, message='您的token已过期，请重新登录')
    user_id = jwt_dict.get('user_id', None)
    if user_id:
        _thread_local.user = SimpleLazyObject(lambda: get_user_model().objects.get(id=user_id))

# 1.注意可以不传sender，为监听所有模型，这里来记录日志
# 2.使用get_current_user()获取当前请求用户
@receiver(post_save)
def post_save_handler(sender, instance, created, **kwargs):
    """模型新增-操作日志填写"""
    # 注意排除日志模块、用例步骤表、测试项步骤表
    if (sender == TableOperationLog or sender == CaseStep or sender == TestDemandContent or sender == LoginLog or sender == OperationLog or sender
            == Users):
        return
    user = get_current_user()
    ope_dict = {
        'operate_obj': str(instance),
    }
    if created:
        ope_dict['operate_des'] = '新增'
    else:
        ope_dict['operate_des'] = '修改'
    log_manager.create(user=user, **ope_dict)

@receiver(post_delete)
def post_delete_handler(sender, instance, **kwargs):
    """模型删除-操作日志填写"""
    # 注意排除日志模块、用例步骤表、测试项步骤表
    if (sender == TableOperationLog or sender == CaseStep or sender == TestDemandContent or sender == LoginLog or sender == OperationLog or sender
            == Users):
        return
    user = get_current_user()
    ope_dict = {
        'operate_obj': str(instance),
        'operate_des': '删除'
    }
    log_manager.create(user=user, **ope_dict)
