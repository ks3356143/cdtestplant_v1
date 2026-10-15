@echo off
chcp 65001 >nul
echo 停止 HTTPS 反向代理...
cd /d %~dp0..\..\packagesInitialize\nginx-1.28.0
nginx -c "%~dp0nginx_https.conf" -s stop
echo 已停止。
