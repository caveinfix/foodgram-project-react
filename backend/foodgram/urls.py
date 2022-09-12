from django.contrib import admin
from django.contrib.staticfiles import views
from django.urls import path, include, re_path
from django.conf import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
]

if settings.DEBUG:
    urlpatterns += [
        re_path(r"^media/(?P<path>.*)$", views.serve),
    ]
