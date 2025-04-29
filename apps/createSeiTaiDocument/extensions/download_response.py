import os, io
from typing import List
import zipfile
from pathlib import Path
from django.conf import settings
from utils.path_utils import project_path
from utils.chen_response import ChenResponse
from django.http import FileResponse, HttpResponse

main_download_path = Path(settings.BASE_DIR) / 'media'

def get_file_respone(id: int, file_name: str | List[str]):
    """将生成文档下载响应"""
    # 1.如果传入的是str，直接是文件名
    if isinstance(file_name, str):
        file_name = "".join([file_name, '.docx'])
        file_abs_path = main_download_path / project_path(id) / 'final_seitai' / file_name
        if not file_abs_path.is_file():
            return ChenResponse(status=404, code=404, message="文档未生成或生成错误！")
        response = FileResponse(open(file_abs_path, 'rb'))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = f"attachment; filename={file_name}.docx"
        return response
    # 2.如果传入的是列表，多个文件名
    elif isinstance(file_name, list):
        file_name_list = file_name
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for file_name in file_name_list:
                file_name = "".join([file_name, '.docx'])
                file_abs_path = main_download_path / project_path(id) / 'final_seitai' / file_name
                zip_file.write(file_abs_path, os.path.basename(file_abs_path))
        zip_buffer.seek(0)
        response = HttpResponse(zip_buffer, content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="回归测试说明文档.zip"'
        return response
    else:
        return ChenResponse(code=500, status=500, message='下载文档出现错误，确认是否有多个轮次内容')
