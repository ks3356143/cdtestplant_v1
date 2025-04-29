#!/usr/bin/env python
import os
import sys

def main():
    # 设置开发环境的django的环境变量(必要)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cdtestplant_v1.dev_settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "无法导入Django. 请确定您是否安装Django and "
            "并确认您的环境变量 PYTHONPATH 是否设置? 您是否忘记 "
            "进入含有Djangod虚拟环境?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
