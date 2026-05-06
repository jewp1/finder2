import logging

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.likes.models import Like
from apps.matches.models import Match

User = get_user_model()
logger = logging.getLogger(__name__)

_USER_FIELDS = [
    "id",
    "username",
    "full_name",
    "bio",
    "skills",
    "experience",
    "is_active",
    "created_at",
    "updated_at",
]


def _user_dict(user):
    return {f: getattr(user, f) for f in _USER_FIELDS}


def _project_dict(project):
    return {
        "id": project.id,
        "title": project.title,
        "description": project.description,
        "requirements": project.requirements,
        "budget": project.budget,
        "duration": project.duration,
        "status": project.status,
        "owner_id": project.owner_id,
        "created_at": project.created_at,
        "updated_at": project.updated_at,
    }


class MatchListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        matches = Match.objects.filter(user=request.user).select_related("liked_user", "project")
        seen_users = set()
        seen_projects = set()
        result = []

        for match in matches:
            if match.liked_user_id and match.liked_user_id not in seen_users:
                seen_users.add(match.liked_user_id)
                result.append(
                    {
                        "id": match.id,
                        "status": match.status,
                        "created_at": match.created_at,
                        "user": _user_dict(match.liked_user),
                    }
                )
            elif match.project_id and match.project_id not in seen_projects:
                seen_projects.add(match.project_id)
                result.append(
                    {
                        "id": match.id,
                        "status": match.status,
                        "created_at": match.created_at,
                        "project": _project_dict(match.project),
                    }
                )

        return Response(result)


class PotentialMatchesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        existing_match_ids = set(
            Match.objects.filter(user=request.user).exclude(liked_user=None).values_list("liked_user_id", flat=True)
        )
        existing_like_ids = set(
            Like.objects.filter(user=request.user).exclude(liked_user=None).values_list("liked_user_id", flat=True)
        )
        excluded_ids = existing_match_ids | existing_like_ids

        users = User.objects.exclude(id=request.user.id).exclude(id__in=excluded_ids)
        result = [_user_dict(u) for u in users]
        return Response(result)


class CreateMatchView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        target = get_object_or_404(User, pk=user_id)

        match = Match.objects.create(
            user=request.user,
            liked_user=target,
            status=Match.STATUS_PENDING,
        )
        logger.info("Match created: id=%s from=%s to=%s", match.id, request.user.id, user_id)

        reverse_like = Like.objects.filter(
            user=target,
            liked_user=request.user,
        ).first()
        if reverse_like and not reverse_like.is_mutual:
            own_like = Like.objects.filter(
                user=request.user,
                liked_user=target,
            ).first()
            if own_like:
                own_like.is_mutual = True
                own_like.save(update_fields=["is_mutual"])
            reverse_like.is_mutual = True
            reverse_like.save(update_fields=["is_mutual"])

        return Response(
            {
                "id": match.id,
                "status": match.status,
                "created_at": match.created_at,
                "user": _user_dict(target),
            },
            status=status.HTTP_201_CREATED,
        )


class UpdateMatchStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, match_id):
        match = get_object_or_404(Match, pk=match_id, user=request.user)
        new_status = request.data.get("status")
        valid = [Match.STATUS_PENDING, Match.STATUS_ACCEPTED, Match.STATUS_REJECTED]
        if new_status not in valid:
            return Response(
                {"detail": f"Status must be one of: {valid}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        match.status = new_status
        match.save(update_fields=["status", "updated_at"])
        logger.info("Match status updated: id=%s status=%s user=%s", match_id, new_status, request.user.id)
        return Response({"id": match.id, "status": match.status})
