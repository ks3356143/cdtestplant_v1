from django.urls import path,re_path
from cdtestplant_v1 import settings
from utils.media_view import protected_media
from .api import api

urlpatterns = [
    path("api/",api.urls),
    # 本地媒体文件：需携带有效 JWT（7.1.8 保密性 / 7.1.3 访问控制）
    re_path(r'uploads/(?P<path>.*)$', protected_media),
]
