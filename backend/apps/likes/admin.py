from django.contrib import admin

from apps.likes.models import Like


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ["user", "liked_user", "project", "is_mutual", "created_at"]
    list_filter = ["is_mutual"]
