from django.contrib import admin
from apps.user.models import Users

# 在这里将数据库表注册到admin中
admin.site.register([Users])

