from django.contrib import admin
from django.urls import path, include
from apps.users.views import RootView, HealthView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RootView.as_view()),
    path('health', HealthView.as_view()),
    path('api/v1/', include('apps.users.urls')),
    path('api/v1/', include('apps.projects.urls')),
    path('api/v1/', include('apps.likes.urls')),
    path('api/v1/', include('apps.matches.urls')),
]
