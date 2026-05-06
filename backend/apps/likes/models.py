from django.conf import settings
from django.db import models
from django_prometheus.models import ExportModelOperationsMixin


class Like(ExportModelOperationsMixin("like"), models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="likes_given",
    )
    liked_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="likes_received",
        null=True,
        blank=True,
    )
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="likes",
        null=True,
        blank=True,
    )
    is_mutual = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "likes"

    def __str__(self):
        return f"Like by user {self.user_id}"
