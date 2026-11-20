# 内网一键部署

把平台打成「拷过去就能用」的离线部署包。目标：内网 Windows 10/11 x64 机器，双击
`一键启动.bat` → MySQL / Redis / 后端 / nginx 全部拉起并自动打开登录页，全程离线、无需安装任何软件。

## 打包（只在开发机跑）

```bash
powershell -NoProfile -ExecutionPolicy Bypass -File 内网一键部署/build_package.ps1
```

产物：`<项目根>/cdtestplant-offline/`（约 2GB，已 gitignore），整文件夹拷到内网机器的**纯英文路径**（如 `D:\cdtestplant`）即可——MySQL 8.4 便携版不吃中文路径，一键启动脚本里已带拦截提示。
脚本做的事：拷贝便携 CPython 3.13 + `.venv` 全部依赖、便携 MySQL（含现成 data 目录）、Redis、
nginx；前端按 `build:intranet` 模式构建并放入 `nginx/html/dist`；后端源码 + 自动生成 `app/.env`
（随机 DJANGO_SECRET_KEY，FIELD_ENCRYPTION_KEY 沿用本机 .env 以保证历史密文可解）+ collectstatic；
最后做依赖导入自检。

## 代码更新后

改了后端/前端代码 → 重跑打包脚本 → 把新的「内网部署包」拷过去覆盖，但**不要覆盖目标机的
`mysql-8.4.3-winx64/data` 目录**（那是目标机的业务数据）。详见包内 `部署说明.md`。
