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

rem If already running, just open the page again.
%SystemRoot%\System32\curl.exe -s -o nul --connect-timeout 2 http://127.0.0.1:8181/
if %errorlevel%==0 (
    echo Already running, opening the page.
    start http://127.0.0.1:8181/
    pause
    exit /b 0
)

echo [1/5] starting MySQL on 3307 ...
start "MySQL-3307" /min /d "%~dp0mysql-8.4.3-winx64\bin" mysqld.exe "--defaults-file=%~dp0mysql-8.4.3-winx64\my.ini" --console

echo [2/5] starting Redis on 6379 ...
start "Redis-6379" /min /d "%~dp0redis" redis-server.exe

echo [3/5] waiting for MySQL, up to 30s ...
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

:MYSQL_OK
echo [4/5] starting backend waitress on 8000 ...
start "backend-8000" /min /d "%~dp0app" "%~dp0python\python.exe" run.py

echo waiting for backend, up to 60s ...
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

:BE_OK
echo [5/5] starting nginx on 8181 and opening the page ...
start "nginx-8181" /min /d "%~dp0nginx-1.28.0" nginx.exe
ping -n 3 127.0.0.1 >nul
start http://127.0.0.1:8181/

echo.
echo All services are up.
echo Local:      http://127.0.0.1:8181/
echo Colleagues: http://YOUR-LAN-IP:8181/   (run: ipconfig)
echo.
pause
