from django.contrib import admin

from apps.matches.models import Match


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ["user", "liked_user", "project", "status", "created_at"]
    list_filter = ["status"]
