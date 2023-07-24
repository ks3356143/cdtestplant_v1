from django.contrib.auth import get_user_model
from datetime import datetime
from ninja_extra.searching import searching
from ninja_extra import api_controller, ControllerBase, status, route
from ninja.pagination import paginate
from ninja import Query
from ninja_jwt.tokens import AccessToken, RefreshToken
from ninja_jwt.authentication import JWTAuth
from ninja_jwt.controller import TokenObtainPairController
from ninja_jwt import schema
from typing import List

from utils.chen_response import ChenResponse
from utils.chen_pagination import MyPagination
from apps.user.schema import UserInfoOutSchema, CreateUserSchema, CreateUserOutSchema, UserRetrieveInputSchema, \
    UserRetrieveOutSchema

Users = get_user_model()
# 定义用户登录接口，包含token刷新和生成
@api_controller("/system", tags=['用户token控制和登录接口'])
class UserTokenController(TokenObtainPairController):
    auto_import = True

    @route.post("/login", url_name='login')
    def obtain_token(self, user_token: schema.TokenObtainPairSerializer):
        user = user_token._user
        token = AccessToken.for_user(user)
        refresh = RefreshToken.for_user(user)
        # 这里完成了用户认证了，用户找不到则jwt自动报错401
        return ChenResponse(code=200,
                            data={'token': str(token), 'refresh': str(refresh),
                                  'token_exp_data': datetime.utcfromtimestamp(token["exp"])})
        # 这里自带一个/refresh接口，为默认的

    @route.get("/getInfo", response=UserInfoOutSchema, url_name="get_info", auth=JWTAuth())
    def get_user_info(self):
        # 直接按照Schema返回
        return self.context.request.auth

    @route.post("/logout", url_name="logout", auth=JWTAuth())
    def logout(self):
        return ChenResponse(code=200, message='退出登录成功')


# 定义system/user用户管理接口
@api_controller("/system/user", tags=['用户管理'], auth=JWTAuth())
class UserManageController(ControllerBase):
    # 用户创建接口
    @route.post("/save", response={201: CreateUserOutSchema}, url_name="user_create", auth=None)
    def create_user(self, user_schema: CreateUserSchema):
        user = user_schema.create()
        return user

    # 用户检索接口
    @route.get("/index", response=List[UserRetrieveOutSchema])
    @paginate(MyPagination)
    def list_user(self, filters: UserRetrieveInputSchema = Query(...)):
        # 重要，因为前端会传空字符
        for attr, value in filters.__dict__.items():
            if getattr(filters, attr) is None:
                setattr(filters, attr, '')
        start_time = self.context.request.GET.get('create_datetime[0]')
        if start_time is None:
            start_time = "2000-01-01"
        end_time = self.context.request.GET.get('create_datetime[1]')
        if end_time is None:
            end_time = '8000-01-01'
        date_list = [start_time, end_time]
        qs = Users.objects.filter(name__icontains=filters.name, username__icontains=filters.username,
                                  phone__icontains=filters.phone, status__contains=filters.status,
                                  create_datetime__range=date_list).order_by('-create_datetime')
        return qs