from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles import views
from django.urls import include, path, re_path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
]

if settings.DEBUG:
    urlpatterns += [
        re_path(r"^media/(?P<path>.*)$", views.serve),
    ]
