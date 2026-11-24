@echo off
title neiwu-cdtestplant - START
rem All-ASCII on purpose: cmd parsing of UTF-8/GBK mixed bats is fragile.
rem Chinese instructions live in bu-shu-shuo-ming.md beside this file.
cd /d "%~dp0"

rem MySQL 8.4 portable build cannot run from a path containing non-ASCII chars.
powershell -NoProfile -Command "if ('%~dp0' -cmatch '[^\x00-\x7F]') { exit 1 }"
if %errorlevel%==1 (
    echo [ERROR] Package folder path contains non-ASCII characters: %~dp0
    echo Please move the whole folder to an ASCII path such as D:\cdtestplant , then retry.
    pause
    exit /b 1
)

rem Each service is detected separately and only missing ones are started, so it
rem is safe to re-run this script after manually closing any console window.

echo [1/4] MySQL on 3307 ...
"%~dp0mysql-8.4.3-winx64\bin\mysqladmin.exe" -h127.0.0.1 -P3307 -uroot -proot ping >nul 2>&1
if %errorlevel%==0 goto MYSQL_SKIP
start "MySQL-3307" /min /d "%~dp0mysql-8.4.3-winx64\bin" mysqld.exe "--defaults-file=%~dp0mysql-8.4.3-winx64\my.ini" --console
set /a TRIES=0
:WAIT_MYSQL
"%~dp0mysql-8.4.3-winx64\bin\mysqladmin.exe" -h127.0.0.1 -P3307 -uroot -proot ping >nul 2>&1
if %errorlevel%==0 goto MYSQL_OK
set /a TRIES+=1
if %TRIES% geq 30 goto MYSQL_FAIL
rem ping delay instead of timeout.exe: timeout needs a real console stdin
ping -n 2 127.0.0.1 >nul
goto WAIT_MYSQL

:MYSQL_FAIL
echo MySQL is not ready in 30s. Check the minimized MySQL window for errors.
pause
exit /b 1

:MYSQL_SKIP
echo       MySQL already running, skip.
goto REDIS_STEP

:MYSQL_OK
echo       MySQL is up.

:REDIS_STEP
echo [2/4] Redis on 6379 ...
"%~dp0redis\redis-cli.exe" -h 127.0.0.1 -p 6379 ping 2>nul | %SystemRoot%\System32\find.exe "PONG" >nul
if %errorlevel%==0 goto REDIS_SKIP
rem bare redis-server.exe dies silently on some Win10 machines: always start with the bundled conf
start "Redis-6379" /min /d "%~dp0redis" redis-server.exe redis.windows.conf
set /a TRIES=0
:WAIT_REDIS
"%~dp0redis\redis-cli.exe" -h 127.0.0.1 -p 6379 ping 2>nul | %SystemRoot%\System32\find.exe "PONG" >nul
if %errorlevel%==0 goto REDIS_OK
set /a TRIES+=1
if %TRIES% geq 15 goto REDIS_FAIL
ping -n 2 127.0.0.1 >nul
goto WAIT_REDIS

:REDIS_FAIL
echo Redis is not ready in 15s. Check the minimized Redis-6379 window for errors.
pause
exit /b 1

:REDIS_SKIP
echo       Redis already running, skip.
goto BE_STEP

:REDIS_OK
echo       Redis is up.

:BE_STEP
echo [3/4] backend waitress on 8000 ...
%SystemRoot%\System32\curl.exe -s -o nul --connect-timeout 2 http://127.0.0.1:8000/api/docs
if %errorlevel%==0 goto BE_SKIP
start "backend-8000" /min /d "%~dp0app" "%~dp0python\python.exe" run.py
set /a TRIES=0
:WAIT_BE
%SystemRoot%\System32\curl.exe -s -o nul --connect-timeout 2 http://127.0.0.1:8000/api/docs
if %errorlevel%==0 goto BE_OK
set /a TRIES+=1
if %TRIES% geq 60 goto BE_FAIL
ping -n 2 127.0.0.1 >nul
goto WAIT_BE

:BE_FAIL
echo Backend is not ready in 60s. Check the minimized backend-8000 window for errors.
pause
exit /b 1

:BE_SKIP
echo       Backend already running, skip.
goto NGINX_STEP

:BE_OK
echo       Backend is up.

:NGINX_STEP
echo [4/4] nginx on 8181 ...
%SystemRoot%\System32\curl.exe -s -o nul --connect-timeout 2 http://127.0.0.1:8181/
if %errorlevel%==0 goto NGINX_SKIP
start "nginx-8181" /min /d "%~dp0nginx-1.28.0" nginx.exe
set /a TRIES=0
:WAIT_NGINX
%SystemRoot%\System32\curl.exe -s -o nul --connect-timeout 2 http://127.0.0.1:8181/
if %errorlevel%==0 goto NGINX_OK
set /a TRIES+=1
if %TRIES% geq 15 goto NGINX_FAIL
ping -n 2 127.0.0.1 >nul
goto WAIT_NGINX

:NGINX_FAIL
echo nginx is not ready in 15s. Check the minimized nginx window for errors.
pause
exit /b 1

:NGINX_SKIP
echo       nginx already running, skip.
goto OPEN

:NGINX_OK
echo       nginx is up.

:OPEN
start http://127.0.0.1:8181/

echo.
echo All services are up.
echo Local:      http://127.0.0.1:8181/
echo Colleagues: http://YOUR-LAN-IP:8181/   (run: ipconfig)
echo.
pause
