import json

from rest_framework import serializers

from apps.projects.models import Project
from apps.users.serializers import UserSerializer


class RequirementsField(serializers.Field):
    def to_representation(self, value):
        if not value:
            return []
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, list) else [value]
        except (json.JSONDecodeError, TypeError):
            return [value]

    def to_internal_value(self, data):
        if isinstance(data, list):
            return json.dumps(data)
        if isinstance(data, str):
            try:
                json.loads(data)
                return data
            except json.JSONDecodeError:
                items = [r.strip() for r in data.split(",") if r.strip()]
                return json.dumps(items)
        return json.dumps([])


class ProjectSerializer(serializers.ModelSerializer):
    owner_id = serializers.IntegerField(source="owner.id", read_only=True)
    requirements = RequirementsField(allow_null=True, required=False)

    class Meta:
        model = Project
        fields = [
            "id",
            "title",
            "description",
            "requirements",
            "budget",
            "duration",
            "status",
            "owner_id",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "owner_id", "created_at", "updated_at"]


class ProjectWithOwnerSerializer(ProjectSerializer):
    owner = UserSerializer(read_only=True)

    class Meta(ProjectSerializer.Meta):
        fields = ProjectSerializer.Meta.fields + ["owner"]
