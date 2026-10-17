from django.contrib.auth import get_user_model
from datetime import datetime, timedelta, timezone
from ninja_extra import api_controller, ControllerBase, route
from ninja.errors import HttpError
from ninja.pagination import paginate
from utils.chen_pagination import MyPagination
from ninja_extra.permissions import IsAuthenticated
from utils.permissions import IsAuditor, IsSystemAdmin
from ninja import Query
from django.db import transaction
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from ninja_jwt.authentication import JWTAuth
from ninja_jwt.controller import TokenObtainPairController
from ninja_jwt import schema
from typing import List
from utils.chen_response import ChenResponse
from apps.user.schema import UserInfoOutSchema, CreateUserSchema, CreateUserOutSchema, \
    UserRetrieveInputSchema, \
    UserRetrieveOutSchema, UpdateDeleteUserSchema, UpdateDeleteUserOutSchema, DeleteUserSchema, LogOutSchema, \
    LogInputSchema, LogDeleteInSchema, AdminModifyPasswordSchema, MyTokenObtainPairOutSchema, \
    MyTokenObtainPairInputSchema
from apps.user.models import TableOperationLog, Users as UserClass
from apps.project.models import Project
# 工具函数
from utils.chen_crud import multi_delete
from apps.user.tools.ldap_tools import load_ldap_users
from utils.audit import audit_log, EVENT_USER_CHANGE
from utils.permissions import PRIVILEGED_ROLES
from utils.codes import HTTP_CAPTCHA_REQUIRED

Users = get_user_model()


def _generate_captcha_svg(code: str) -> str:
    """生成 4 位图形验证码 SVG（不依赖 Pillow）"""
    import random
    chars = []
    for i, ch in enumerate(code):
        x = 14 + i * 22 + random.randint(-3, 3)
        y = 30 + random.randint(-4, 4)
        rotate = random.randint(-18, 18)
        color = f"#{random.randint(30,120):02x}{random.randint(30,120):02x}{random.randint(30,120):02x}"
        chars.append(f'<text x="{x}" y="{y}" font-size="24" font-weight="bold" fill="{color}" '
                     f'transform="rotate({rotate} {x} {y})" font-family="Arial">{ch}</text>')
    lines = []
    for _ in range(4):
        x1, y1, x2, y2 = random.randint(0, 100), random.randint(0, 44), random.randint(0, 100), random.randint(0, 44)
        lines.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
                     f'stroke="#{random.randint(100,200):02x}{random.randint(100,200):02x}{random.randint(100,200):02x}" stroke-width="1"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="104" height="44">'
            f'<rect width="100%" height="100%" fill="#f2f3f5"/>{"".join(lines)}{"".join(chars)}</svg>')


def _verify_login_captcha(captcha_key: str, captcha_code: str):
    """特权角色登录双因子：校验图形验证码（一次性，Redis 5 分钟有效）"""
    from django.core.cache import cache
    if not captcha_key or not captcha_code:
        raise HttpError(40001, "特权账号登录需要图形验证码，请刷新后输入")
    real_code = cache.get(f'captcha:{captcha_key}')
    cache.delete(f'captcha:{captcha_key}')  # 一次性使用，防重放
    if not real_code or str(real_code).lower() != str(captcha_code).strip().lower():
        raise HttpError(40001, "验证码错误或已过期，请刷新后重试")

# 定义用户登录接口，包含token刷新和生成
@api_controller("/system", tags=['用户token控制和登录接口'])
class UserTokenController(TokenObtainPairController):
    auto_import = True

    @route.post("/login", response=MyTokenObtainPairOutSchema, url_name='login')
    def obtain_token(self, user_token: MyTokenObtainPairInputSchema):
        # 三权分立：特权角色（系统管理员/安全员/审计员）登录强制双因子——口令 + 图形验证码
        # （鉴别失败处置在 schema.authenticate() 挂钩：锁定检查/失败累计/成功清零）
        login_user = Users.objects.filter(username=user_token.username).first()
        if login_user and getattr(login_user, 'role', None) in PRIVILEGED_ROLES:
            # 未带验证码：以业务码请前端按需显示验证码输入框（登录页默认不显示，
            # 普通用户零影响；不设探测接口，特权账号名单不可被枚举）
            if not user_token.captcha_key or not user_token.captcha_code:
                return ChenResponse(code=HTTP_CAPTCHA_REQUIRED, data={'need_captcha': True},
                                    message='该账号登录需要图形验证码，请输入后重试')
            _verify_login_captcha(user_token.captcha_key, user_token.captcha_code)
        user_token.check_user_authentication_rule()
        return user_token.to_response_schema()

    @route.get("/captcha", url_name='captcha', auth=None)
    def get_captcha(self):
        """图形验证码获取：返回 captcha_key 与 base64 SVG 图片，5 分钟有效"""
        import random
        import uuid
        import base64
        from django.core.cache import cache
        chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
        code = ''.join(random.choices(chars, k=4))
        captcha_key = uuid.uuid4().hex
        cache.set(f'captcha:{captcha_key}', code, 300)
        svg_b64 = base64.b64encode(_generate_captcha_svg(code).encode('utf-8')).decode('ascii')
        return ChenResponse(data={'captcha_key': captcha_key, 'image': f'data:image/svg+xml;base64,{svg_b64}'})

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
                permissions=[IsAuthenticated, IsSystemAdmin])
    def create_user(self, user_schema: CreateUserSchema):
        user = user_schema.create()
        # 审计留痕（7.1.6：账号注册/权限授予）
        audit_log(self.context.request, EVENT_USER_CHANGE,
                  f'账号创建：新建用户 {user.username}（{user.name}），角色 {getattr(user, "role", "") or "user"}')
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

    # 用户检索接口（仅系统管理员：三权分立，普通用户/安全员/审计员无账号管理权）
    @route.get("/index", response=List[UserRetrieveOutSchema], permissions=[IsAuthenticated, IsSystemAdmin])
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

    @route.put("/update/{user_id}", response=UpdateDeleteUserOutSchema,
               permissions=[IsAuthenticated, IsSystemAdmin],
               url_name="user-update")
    def update_user(self, user_id: int, payload: UpdateDeleteUserSchema):
        if payload.username == "superAdmin":
            return ChenResponse(code=400, status=400, message="无法编辑，唯一管理员账号")
        payload.validate_unique_username(user_id)
        # 一次查询拿到旧角色并就地更新（避免 audit 埋点带来的额外 SELECT）
        target = get_object_or_404(Users, id=user_id)
        old_role = target.role
        for attr, value in payload.dict().items():
            setattr(target, attr, value)
        target.save()
        # 审计留痕（7.1.6：账号信息/权限变更）
        role_part = f'，角色 {old_role} → {target.role}' if old_role != target.role else ''
        audit_log(self.context.request, EVENT_USER_CHANGE,
                  f'账号修改：用户 {target.username}{role_part}')
        return {"message": "用户更新成功"}

    @route.delete("/delete", permissions=[IsAuthenticated, IsSystemAdmin], url_name="user-delete")
    def delete_user(self, data: DeleteUserSchema):
        # 保护创始人：剔除 id=1 后再删（注意不能在迭代中 pop 列表元素——会跳过元素）
        ids = [i for i in data.ids if i != 1]
        usernames = list(Users.objects.filter(id__in=ids).values_list('username', flat=True))
        multi_delete(ids, Users)
        # 审计留痕（7.1.6：账号注销/权限回收）
        audit_log(self.context.request, EVENT_USER_CHANGE, f'账号删除：注销用户 {usernames or ids}')
        return ChenResponse(code=200, status=200, message="删除成功")

    # 管理员改变用户状态是否停用/启用
    @route.get('/change_status', auth=JWTAuth(), permissions=[IsAuthenticated, IsSystemAdmin],
               url_name='user-change')
    def change_user_status(self, user_status: str, userId: int):
        user = Users.objects.filter(id=userId).first()
        if not user:
            return ChenResponse(status=400, code=400, message='用户未找到')
        if user.id == 1:
            return ChenResponse(status=400, code=400, message='管理员不能被禁用，此操作无效')
        user.status = user_status
        user.save()
        # 审计留痕（7.1.6：账号启用/禁用）
        state = '启用' if str(user_status) == '1' else '禁用'
        audit_log(self.context.request, EVENT_USER_CHANGE, f'账号状态变更：{state}用户 {user.username}')
        return user.status

    # 用户自助修改本人密码（旧密码校验，登录用户均可操作）
    @route.post("/modifyPassword", auth=JWTAuth(), permissions=[IsAuthenticated])
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
        return None

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
    @route.get("/operation_list", url_name="log_list", response=List[LogOutSchema],
               permissions=[IsAuthenticated, IsAuditor])
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

    @route.get('/operation_delete', url_name='log_delete', permissions=[IsAuthenticated, IsAuditor],
               auth=JWTAuth())
    def log_delete(self, data: LogDeleteInSchema = Query(...)):
        time = datetime.now() - timedelta(days=data.day)
        log_qs = TableOperationLog.objects.filter(create_datetime__lt=time)
        log_qs.delete()
        if data.day > 0:
            return ChenResponse(message=f'删除{data.day}天前数据成功')
        else:
            return ChenResponse(message='全部日志删除成功')
