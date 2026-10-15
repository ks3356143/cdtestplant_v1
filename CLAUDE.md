# CLAUDE.md

测试管理平台（cdtestplant_v1）：后端 Python + Django Ninja，前端 Vue 3。代码注释、文档、UI 均为中文。

## 项目结构

- **后端（根目录）**：Django 6 + django-ninja + ninja-extra + ninja-jwt，Python 3.13，包管理用 `uv`（见 pyproject.toml / uv.lock，虚拟环境在 .venv/）
- **前端**：`web/cdTMP/`，Vue 3.5 + Vite 8 + TypeScript + Arco Design Vue + Tailwind CSS 4 + Pinia + Vue Router + TanStack vue-query + axios
- `conf/`：环境配置（env.py 含 MySQL/Redis/LDAP/Celery 配置）、ninja_extra_settings、logConfig
- `utils/`：公共库 —— `chen_ninja.py`（自定义 API 类）、`chen_response.py`（统一响应）、`chen_crud.py`、`chen_pagination.py`、`codes.py`（自定义错误码）、`models.py`、`log_util/`、`chapter_tools/`、`smallTools/`
- `media/`：生成的文档、表单模板（form_template、final_seitai 等按项目 R 号存放）
- `apps/` 下各应用：user（用户）、dict（字典）、system（系统）、project（项目/用例/问题单等）、createDocument（生成评测文档）、createSeiTaiDocument（生成正态文档）

## 后端约定

- API 全部挂在 `cdtestplant_v1/urls.py` 的 `path("api/", api.urls)` 下，`cdtestplant_v1/api.py` 中 `api.auto_discover_controllers()` 自动发现各 app 的控制器
- 每个 app 的接口写在 `controllers/` 目录按业务域分文件（如 project 下 case.py、round.py、problem.py…），类用 `@api_controller` 修饰，并在 `controllers/__init__.py` 中统一导入到 `__all__`
- 统一响应格式用 `utils.chen_response.ChenResponse`：`{"code", "data", "message", "success"}`（它返回的是 axios 的 response.data）
- 自定义错误码在 `utils/codes.py`；HttpError 的 status_code 被处理为自定义码而非 HTTP 码（见 api.py 的 exception_handler）
- ORM 序列化用 ninja-schema / pydantic v2；JSON 解析/渲染用自定义 orjson 的 MyParser/MyRenderer
- 数据库 MySQL（库名 chengdu_test_plant_v1，本地 3306 / 打包生产 3307，配置在 conf/env.py），Redis 用于 Celery；认证走 LDAP + ModelBackend
- 文档生成重度使用 python-docx / docxtpl / docxcompose / lxml

## 常用命令

后端（根目录）：
```bash
uv sync                        # 安装依赖
python manage.py runserver     # 开发服务器
python run.py                  # 生产 waitress 服务器（127.0.0.1:8000）
python manage.py makemigrations
python manage.py migrate
```

前端（web/cdTMP/）：
```bash
npm install
npm run dev          # vite 开发服务器
npm run build:dev    # 开发环境构建
npm run build:prod   # 生产环境构建
npm run prettier     # 格式化
```

## 本地运行（Windows 本机，无安装服务）

- **MySQL**：便携版在 `packagesInitialize/mysql-8.4.3-winx64/`（数据目录已初始化）。启动：在该目录 `bin/` 下执行 `./mysqld.exe --console --port=3306`（命令行覆盖 my.ini 的 3307，dev_settings 用 3306）。账号 root/root，库 chengdu_test_plant_v1
- **Redis**：便携版在 `packagesInitialize/redis/`（tporadowski 5.0.14）。启动：`./redis-server.exe --port 6379`。CACHES 用 db 1
- **初始化数据**：`packagesInitialize/dbdata.sql`（5.1MB，含 DROP TABLE，可重复导入）：
  `mysql.exe -uroot -proot -D chengdu_test_plant_v1 --default-character-set=utf8mb4 < packagesInitialize/dbdata.sql`
- **启动顺序**：MySQL → Redis → 后端 → 前端。前后端可用 `.claude/launch.json`（backend: uv run manage.py runserver 8000；frontend: npm --prefix web/cdTMP run dev，端口 3888）
- 后端接口验证：Swagger 在 http://127.0.0.1:8000/api/docs ，登录接口 POST `/api/system/login`
- 前端代理：vite 把 `/api` 代理到 http://127.0.0.1:8000/api（.env.development）
- 注意：LDAP（dns.paisat.cn）和 AI 接口（192.168.0.63:8777）是内网地址，本机不在内网时这些功能不可用；本地登录走数据库用户（ModelBackend）
- Django 6 启动系统检查就会连 MySQL，数据库没起后端直接报 2002 退不了启动阶段

## 其他

- 根目录 `dbdata.sql`（21MB，2026-03 完整导出）是较新的全量备份；packagesInitialize/dbdata.sql 是部署包初始化数据，两者不同
- 前端接口封装在 `web/cdTMP/src/api/`（request.js 为 axios 基础封装，按模块分目录），页面在 `src/views/`（dashboard / datamanage / monitor / project / testmanage）
- 前端环境变量：`web/cdTMP/.env.development`、`.env.production`
- 日志：`logs/root_log`，后端有 ApiLoggingMiddleware 记录接口日志
- settings.py 中有 TODO 标注：生产打包需移除 staticfiles/TEMPLATES 调试项
