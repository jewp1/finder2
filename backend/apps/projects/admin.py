from django.contrib import admin

from apps.projects.models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ["title", "owner", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["title", "description"]
