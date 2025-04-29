from django.contrib.auth import get_user_model
from datetime import datetime, timedelta, timezone
from ninja_extra import api_controller, ControllerBase, route
from ninja.pagination import paginate
from utils.chen_pagination import MyPagination
from ninja_extra.permissions import IsAuthenticated, IsAdminUser
from ninja import Query
from django.db import transaction
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from ninja_jwt.tokens import RefreshToken
from ninja_jwt.authentication import JWTAuth
from ninja_jwt.controller import TokenObtainPairController
from ninja_jwt import schema
from typing import List
from utils.chen_response import ChenResponse
from apps.user.schema import UserInfoOutSchema, CreateUserSchema, CreateUserOutSchema, UserRetrieveInputSchema, \
    UserRetrieveOutSchema, UpdateDeleteUserSchema, UpdateDeleteUserOutSchema, DeleteUserSchema, LogOutSchema, \
    LogInputSchema, LogDeleteInSchema, AdminModifyPasswordSchema
from apps.user.models import TableOperationLog, Users as UserClass
from apps.project.models import Project
# 工具函数
from utils.chen_crud import update, multi_delete
from apps.user.tools.ldap_tools import load_ldap_users
# 导入登录日志函数
from utils.log_util.request_util import save_login_log

Users: UserClass = get_user_model()  # type:ignore

# 定义用户登录接口，包含token刷新和生成
@api_controller("/system", tags=['用户token控制和登录接口'])
class UserTokenController(TokenObtainPairController):
    auto_import = True

    @route.post("/login", url_name='login')
    def obtain_token(self, user_token: schema.TokenObtainPairSerializer):
        """新版本有特性，后期修改"""
        # 注意TokenObtainPairSerializer是老版本，所以兼容，本质是TokenObtainPairInputSchema
        user: UserClass = user_token._user
        if user:
            # 判断是否为启用状态
            if user.status == '2':
                return ChenResponse(status=500, code=500, message='账号已被禁用，请联系管理员...')
            save_login_log(request=self.context.request, user=user)  # 保存登录日志
        refresh = RefreshToken.for_user(user)
        token = refresh.access_token  # type:ignore
        return ChenResponse(code=200,
                            data={'token': str(token), 'refresh': str(refresh),
                                  'token_exp_data': datetime.fromtimestamp(token["exp"], tz=timezone.utc)})

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
    @route.post("/save", response=CreateUserOutSchema, url_name="user_create", auth=JWTAuth(),
                permissions=[IsAuthenticated, IsAdminUser])
    def create_user(self, user_schema: CreateUserSchema):
        user = user_schema.create()
        return user

    # 给前端传所有用户当做字典
    @route.get('/list', response=List[UserRetrieveOutSchema], url_name="user_list", auth=None)
    @transaction.atomic
    def list_user(self, project_id: int = None):
        """如果传了project_id则返回项目中的成员而非全部用户"""
        qs = Users.objects.all()
        if project_id is not None:
            project_obj = get_object_or_404(Project, id=project_id)
            all_member: list = project_obj.member
            # 将member和duty_person联合
            if project_obj.duty_person not in project_obj.member:
                all_member.append(project_obj.duty_person)
            qs = qs.filter(name__in=all_member)
        return qs

    # 用户检索接口
    @route.get("/index", response=List[UserRetrieveOutSchema])
    @paginate(MyPagination)
    def index_user(self, filters: UserRetrieveInputSchema = Query(...)):
        # 重要，处理前端不传值为None的情况
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

    @route.put("/update/{user_id}", response=UpdateDeleteUserOutSchema, permissions=[IsAuthenticated, IsAdminUser],
               url_name="user-update")
    def update_user(self, user_id: int, payload: UpdateDeleteUserSchema):
        if payload.username == "superAdmin":
            return ChenResponse(code=400, status=400, message="无法编辑，唯一管理员账号")
        payload.validate_unique_username(user_id)
        update_user = update(self.context.request, user_id, payload, Users)
        return {"message": "用户更新成功"}

    @route.delete("/delete", permissions=[IsAuthenticated, IsAdminUser], url_name="user-delete")
    def delete_user(self, data: DeleteUserSchema):
        ids = data.ids
        # 去掉删除创始人
        for item in ids:
            if item == 1:
                ids.pop(item)
        multi_delete(ids, Users)
        return ChenResponse(code=200, status=200, message="删除成功")

    # 管理员改变用户状态是否停用/启用
    @route.get('/change_status', auth=JWTAuth(), permissions=[IsAuthenticated, IsAdminUser], url_name='user-change')
    def change_user_status(self, user_status: str, userId: int):
        user = Users.objects.filter(id=userId).first()
        if not user:
            return ChenResponse(status=400, code=400, message='用户未找到')
        if user.id == 1:
            return ChenResponse(status=400, code=400, message='管理员不能被禁用，此操作无效')
        user.status = user_status
        user.save()
        return user.status

    @route.post("/modifyPassword", auth=JWTAuth(), permissions=[IsAuthenticated, IsAdminUser])
    def modify_password(self, payload: AdminModifyPasswordSchema):
        user: UserClass = self.context.request.user  # type:ignore
        if user:
            # 判断就密码是否正确
            user_old = authenticate(username=user.username, password=payload.oldPassword)
            if not user_old:
                return ChenResponse(status=500, code=500, message='旧密码错误，请检查')
            user.set_password(payload.newPassword)
            user.save()
            return ChenResponse(status=200, code=200, message='管理员修改密码成功')

    # 用户登录后动态读取LDAP用户录入数据
    @route.get("/ldap", url_name='user-ldap')
    def load_ldap(self):
        try:
            load_ldap_users()
            return ChenResponse(status=200, code=200, message='连接LDAP服务器成功，同步用户数据')
        except Exception as exc:
            print(exc)
            return ChenResponse(status=200, code=200, message='欢迎您，正在外网访问')

# 操作日志接口
@api_controller("/system/log", tags=['日志记录'], auth=JWTAuth())
class LogController(ControllerBase):
    @route.get("/operation_list", url_name="log_list", response=List[LogOutSchema], auth=None)
    @paginate(MyPagination)
    def log_list(self, data: Query[LogInputSchema]):
        for attr, value in data.model_dump().items():
            if getattr(data, attr) is None:
                setattr(data, attr, '')
        logs = TableOperationLog.objects.values('id', 'user__username', 'operate_obj', 'create_datetime',
                                                'operate_des').order_by(
            '-create_datetime')
        # 根据条件搜索
        logs = logs.filter(user__username__icontains=data.user, create_datetime__range=data.create_datetime)
        return logs

    @route.get('/operation_delete', url_name='log_delete', permissions=[IsAuthenticated, IsAdminUser], auth=JWTAuth())
    def log_delete(self, data: LogDeleteInSchema = Query(...)):
        time = datetime.now() - timedelta(days=data.day)
        log_qs = TableOperationLog.objects.filter(create_datetime__lt=time)
        log_qs.delete()
        if data.day > 0:
            return ChenResponse(message=f'删除{data.day}天前数据成功')
        else:
            return ChenResponse(message='全部日志删除成功')
