from apps.user.models import Users
from ninja_schema import ModelSchema, model_validator, Schema
from ninja_extra.exceptions import APIException
from ninja_extra import status
from datetime import datetime, timezone
from typing import List, Type, Dict
from ninja import Field
from ninja.errors import HttpError
from ninja_jwt.schema import TokenObtainInputSchemaBase
from ninja_jwt.tokens import RefreshToken
from pydantic import model_validator as pydantic_model_validator
from utils.log_util.request_util import save_login_log

UserModel = Users

# 定义用户名异常
class UsernameException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "用户名已存在，注册失败"
    default_code = 400

# schema：作用于创建用户请求
# 注意：不含 clearance——密级标记由系统安全员统一配置（三权分立，GB/T 28452-2012 7.1.5），管理员只管账号
class CreateUserSchema(ModelSchema):
    class Config:
        model = UserModel
        include = ('username', 'name', 'password', 'phone', 'status', 'role',)

    # username判重（精确匹配：子串匹配会把 admin123 误判为与已存在的 admin 重复）
    @model_validator("username")
    @classmethod
    def unique_username(cls, value):
        if UserModel.objects.filter(username=value).exists():
            raise UsernameException()
        return value

    def create(self):
        # 注意这里使用exclude_none，dict()方式属于pydantic
        return UserModel.objects.create_user(**self.dict(exclude_none=True), email='xxx@qq.com')

# schema:作用于创建用户后response
class CreateUserOutSchema(ModelSchema):
    class Config:
        model = UserModel
        exclude = ('password',)

# schema:定义前端查询用户信息的输出
class UserInfoOutSchema(ModelSchema):
    class Config:
        model = UserModel
        exclude = ("password",)

# schema:作用于用户检索以及其他
class UserRetrieveInputSchema(ModelSchema):
    class Config:
        model = UserModel
        include = ("name", "username", "phone", "status",)
        # ninja_schema的可选字段
        optional = ("name", "username", "phone", "status",)

# schema:作用于检索后的输出定义
class UserRetrieveOutSchema(ModelSchema):
    class Config:
        model = UserModel
        exclude = ("password",)

# 删除和更新用户（不含 clearance——密级标记由系统安全员统一配置，见安全策略接口）
class UpdateDeleteUserSchema(ModelSchema):
    class Config:
        model = UserModel
        include = ("name", "username", "phone", "status", "role")

    def validate_unique_username(self, id: int):
        user_filters = UserModel.objects.filter(username=self.username)
        if len(user_filters) > 1:
            raise UsernameException()
        elif len(user_filters) == 1:
            if user_filters[0].id == id:
                return
            else:
                raise UsernameException()
        else:
            return

class UpdateDeleteUserOutSchema(Schema):
    message: str

class DeleteUserSchema(Schema):
    ids: List[int]

# ~~~~~~~~~~~~~~~~~~~~日志schema~~~~~~~~~~~~~~~~~~~~
# 操作日志的schema
class LogOutSchema(Schema):
    id: int
    user: str = Field(..., alias='user__username')
    operate_obj: str
    create_datetime: datetime
    operate_des: str

# 操作日志的查询
class LogInputSchema(Schema):
    user: str = Field("", alias='user')
    create_datetime: List = ['2000-01-01', '9999-01-01']

# 操作日志的删除输入
class LogDeleteInSchema(Schema):
    day: int = Field(30, ge=0, description='删除多少天前的数据（最小保留期 30 天）')

# 管理员修改密码
class AdminModifyPasswordSchema(Schema):
    newPassword: str
    newPassword_confirmation: str
    oldPassword: str

    @pydantic_model_validator(mode='after')
    def check_new_password_confirmation(self):
        # 两次输入的新密码必须一致（原实现声明了确认字段却从未校验）
        if self.newPassword != self.newPassword_confirmation:
            raise ValueError('两次输入的新密码不一致')
        return self

# ~~~~~~~~~~~~~~~~~~~~JWT~~~~~~~~~~~~~~~~~~~~
# 定义输出的内容，修改了输出access变为token，新增token_exp_data字段
class MyTokenObtainPairOutSchema(Schema):
    token: str
    refresh: str
    token_exp_data: datetime

class MyTokenObtainPairInputSchema(TokenObtainInputSchemaBase):
    # 图形验证码（三权分立：特权角色登录双因子，服务端校验）
    captcha_key: str = None
    captcha_code: str = None

    @classmethod
    def get_response_schema(cls) -> Type[Schema]:
        """修改默认的返回Schema"""
        return MyTokenObtainPairOutSchema

    @classmethod
    def get_token(cls, user) -> Dict:
        """因为输出Schema修改，这里修改输出的token字典字段"""
        values = {}
        refresh = RefreshToken.for_user(user)
        token = refresh.access_token
        values["token"] = str(token)  # 修改在这里 # type:ignore
        values['refresh'] = str(refresh)
        values["token_exp_data"] = datetime.fromtimestamp(token["exp"], tz=timezone.utc)
        return values

    def authenticate(self, request, credentials: Dict):
        # 鉴别失败处置（GB/T 28452-2012 7.1.1）：锁定检查 → 失败累计 → 成功清零
        from apps.user.tools.login_security import check_login_locked, record_login_failure, clear_login_failure
        username = credentials.get('username')
        check_login_locked(username)
        try:
            super().authenticate(request, credentials)
        except Exception:
            record_login_failure(username, request)  # 传入 request 以记录来源 IP（7.1.6 审计）
            raise
        clear_login_failure(username)
        if self._user:
            # 先判禁用再记登录日志：避免被禁用账号在审计中留下"登录成功"记录，与结果矛盾
            if self._user.status == '2':  # type:ignore
                raise HttpError(401, "账号已被禁用，请联系管理员...")
            save_login_log(request, self._user)
