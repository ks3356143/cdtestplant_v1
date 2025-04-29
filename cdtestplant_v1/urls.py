from django.urls import path,re_path
from django.views.static import serve
from cdtestplant_v1 import settings
from .api import api

urlpatterns = [
    path("api/",api.urls),
    # 访问静态资源
    re_path(r'uploads/(?P<path>.*)$',serve,{'document_root':settings.MEDIA_ROOT}),
]
