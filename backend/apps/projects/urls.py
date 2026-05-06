from django.urls import path

from apps.projects.views import ProjectDetailView, ProjectListCreateView

urlpatterns = [
    path("projects/", ProjectListCreateView.as_view()),
    path("projects/<int:project_id>", ProjectDetailView.as_view()),
]
