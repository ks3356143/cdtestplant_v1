@echo off

echo 请使用管理员运行该脚本

echo 正在设置环境变量...
set currentDir=%~dp0
set currentDir=%currentDir%mysql-8.4.3-winx64
set basedir=%currentDir%

echo **********当前mysql根路径:%basedir%**********

setx /M PATH "%basedir%bin;%path%"

echo **********初始化数据库配置文件**********
echo **********删除init配置文件**********

del %basedir%\my.ini

echo **********新增init配置文件，注意端口号为3307，这是为了某些安装过mysql的进行回避**********

@echo [mysqld]>>%basedir%\my.ini
@echo port=3307>>%basedir%\my.ini
@echo basedir=%basedir%>>%basedir%\my.ini
@echo datadir=%basedir%\data>>%basedir%\my.ini
@echo max_connections=200>>%basedir%\my.ini
@echo max_connect_errors=10>>%basedir%\my.ini
@echo character-set-server=utf8mb4>>%basedir%\my.ini
@echo default-storage-engine=INNODB>>%basedir%\my.ini
@echo default_authentication_plugin=mysql_native_password>>%basedir%\my.ini
@echo [mysql]>>%basedir%\my.ini
@echo default-character-set=utf8mb4>>%basedir%\my.ini
@echo [client]>>%basedir%\my.ini
@echo default-character-set=utf8mb4>>%basedir%\my.ini
@echo port=3307>>%basedir%\my.ini

echo **********初始化数据库中**********
%basedir%\bin\mysqld.exe --initialize-insecure --lower-case-table-names=1 --user=mysql --console

echo **********开始安装数据库**********
%basedir%\bin\mysqld.exe --install mysql80

echo **********安装服务，后面添加80不和本地mysql服务冲突**********
net start mysql80