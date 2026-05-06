from django.contrib import admin
from django.urls import include, path

from apps.users.views import HealthView, RootView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", RootView.as_view()),
    path("health", HealthView.as_view()),
    path("api/v1/", include("apps.users.urls")),
    path("api/v1/", include("apps.projects.urls")),
    path("api/v1/", include("apps.likes.urls")),
    path("api/v1/", include("apps.matches.urls")),
    path("", include("django_prometheus.urls")),
]
