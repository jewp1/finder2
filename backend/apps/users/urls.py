from django.urls import path
from apps.users.views import RegisterView, LoginView, MeView, UserListView

urlpatterns = [
    path('auth/register', RegisterView.as_view()),
    path('auth/login', LoginView.as_view()),
    path('auth/me', MeView.as_view()),
    path('users/', UserListView.as_view()),
]
