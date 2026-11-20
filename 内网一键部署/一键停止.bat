@echo off
title neiwu-cdtestplant - STOP
rem All-ASCII on purpose: cmd parsing of UTF-8/GBK mixed bats is fragile.
cd /d "%~dp0"

echo [1/4] stopping nginx ...
pushd "%~dp0nginx-1.28.0"
.\nginx.exe -s stop
popd

echo [2/4] stopping backend waitress, matched by this package's python.exe path ...
rem kill by ProcessId: piping a Win32_Process object straight into Stop-Process binds by Name and is unreliable
powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { $_.ExecutablePath -eq '%~dp0python\python.exe' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }"

echo [3/4] stopping MySQL, clean shutdown ...
"%~dp0mysql-8.4.3-winx64\bin\mysqladmin.exe" -h127.0.0.1 -P3307 -uroot -proot shutdown

echo [4/4] stopping Redis ...
"%~dp0redis\redis-cli.exe" shutdown

echo.
echo All services stopped.
pause
