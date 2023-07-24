from apps.user.models import Users
from django.contrib.auth.models import Group
from ninja_schema import ModelSchema, model_validator, Schema
from ninja_extra.exceptions import APIException
from ninja_extra import status
from datetime import datetime
from typing import List, Optional
from utils.chen_response import ChenResponse

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
        include = ('username','email','name','password','phone','status',)

    # username判重
    @model_validator("username")
    def unique_username(cls, value):
        if UserModel.objects.filter(username__icontains=value).exists():
            return ChenResponse(code=400, status=400, message="账号重复，请重新设置")
        return value

    def create(self):
        # 注意这里使用exclude_none，dict()方式属于pydantic
        return UserModel.objects.create_user(**self.dict(exclude_none=True))

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
