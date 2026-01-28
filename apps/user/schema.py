from apps.user.models import Users
from django.contrib.auth.models import Group
from ninja_schema import ModelSchema, model_validator, Schema
from ninja_extra.exceptions import APIException
from ninja_extra import status
from datetime import datetime, timezone
from typing import List, Type, Dict
from ninja import Field
from ninja.errors import HttpError
from ninja_jwt.schema import TokenObtainInputSchemaBase
from ninja_jwt.tokens import RefreshToken
from utils.log_util.request_util import save_login_log

UserModel = Users

# 定义用户名异常
class UsernameException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "用户名已存在，注册失败"
    default_code = 400

class GroupSchema(ModelSchema):
    class Config:
        # 因为保证唯一性，所以ninja_schema使用set集合
        model = Group
        # 注意ninja_schema(include)和ninja(model_fields)
        include = ("name",)

# schema：作用于创建用户请求
class CreateUserSchema(ModelSchema):
    class Config:
        model = UserModel
        include = ('username', 'name', 'password', 'phone', 'status',)

    # username判重
    @model_validator("username")
    @classmethod
    def unique_username(cls, value):
        if UserModel.objects.filter(username__icontains=value).exists():
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

# 删除和更新用户
class UpdateDeleteUserSchema(ModelSchema):
    class Config:
        model = UserModel
        include = ("name", "username", "phone", "status")

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
    day: int = Field(7, ge=0, description='删除多少天前的数据')

# 管理员修改密码
class AdminModifyPasswordSchema(Schema):
    newPassword: str
    newPassword_confirmation: str
    oldPassword: str

# ~~~~~~~~~~~~~~~~~~~~JWT~~~~~~~~~~~~~~~~~~~~
# 定义输出的内容，修改了输出access变为token，新增token_exp_data字段
class MyTokenObtainPairOutSchema(Schema):
    token: str
    refresh: str
    token_exp_data: datetime

class MyTokenObtainPairInputSchema(TokenObtainInputSchemaBase):
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
        super().authenticate(request, credentials)
        if self._user:
            save_login_log(request, self._user)
            if self._user.status == '2':  # type:ignore
                raise HttpError(401, "账号已被禁用，请联系管理员...")
