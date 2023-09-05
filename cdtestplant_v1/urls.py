from django.contrib import admin
from django.urls import path,re_path
from django.views.static import serve
from cdtestplant_v1 import settings
from .api import api

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/",api.urls),
    # 这样可以url访问路径
    re_path(r'media/(?P<path>.*)$',serve,{'document_root':settings.MEDIA_ROOT}),
]
