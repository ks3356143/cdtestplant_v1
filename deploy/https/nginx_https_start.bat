@echo off
chcp 65001 >nul
echo 启动 HTTPS 反向代理（nginx 8443，自签名证书）...
cd /d %~dp0..\..\packagesInitialize\nginx-1.28.0
start nginx -c "%~dp0nginx_https.conf"
echo 启动完成：https://localhost:8443 （前端构建产物需先复制到 nginx-1.28.0\html\dist）
echo 停止请运行 nginx_https_stop.bat
