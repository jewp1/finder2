import logging

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.likes.models import Like
from apps.matches.models import Match
from apps.projects.models import Project
from apps.users.serializers import UserSerializer

User = get_user_model()
logger = logging.getLogger(__name__)

_USER_FIELDS = [
    "id",
    "email",
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


class LikeUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        target = get_object_or_404(User, pk=user_id)

        if request.user.id == user_id:
            return Response({"detail": "Cannot like yourself"}, status=status.HTTP_400_BAD_REQUEST)

        like, created = Like.objects.get_or_create(
            user=request.user,
            liked_user=target,
            defaults={"is_mutual": False},
        )
        if created:
            logger.info("User liked: from=%s to=%s", request.user.id, user_id)

        reverse = Like.objects.filter(
            user=target,
            liked_user=request.user,
        ).first()
        if reverse and not like.is_mutual:
            like.is_mutual = True
            like.save(update_fields=["is_mutual"])
            reverse.is_mutual = True
            reverse.save(update_fields=["is_mutual"])
            Match.objects.get_or_create(
                user=request.user,
                liked_user=target,
                defaults={"status": Match.STATUS_ACCEPTED},
            )
            Match.objects.get_or_create(
                user=target,
                liked_user=request.user,
                defaults={"status": Match.STATUS_ACCEPTED},
            )
            logger.info("Mutual match created: user=%s user=%s", request.user.id, user_id)

        return Response({"message": "Like created successfully"})


class UserLikesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        likes = Like.objects.filter(
            user=request.user,
            liked_user__isnull=False,
        ).select_related("liked_user")

        result = []
        for like in likes:
            result.append(
                {
                    "id": like.id,
                    "is_mutual": like.is_mutual,
                    "created_at": like.created_at,
                    "user": _user_dict(like.liked_user),
                }
            )
        return Response(result)


class UserLikedByView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        likes = Like.objects.filter(
            liked_user=request.user,
        ).select_related("user")

        result = []
        for like in likes:
            result.append(
                {
                    "id": like.id,
                    "is_mutual": like.is_mutual,
                    "created_at": like.created_at,
                    "user": _user_dict(like.user),
                }
            )
        return Response(result)


class LikeProjectView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, project_id):
        project = get_object_or_404(Project, pk=project_id)
        like, created = Like.objects.get_or_create(
            user=request.user,
            project=project,
            defaults={"is_mutual": False},
        )
        if created:
            logger.info("Project liked: user=%s project=%s", request.user.id, project_id)
        return Response({"message": "Project liked successfully", "like_id": like.id})


class LikeMatchesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        likes = Like.objects.filter(
            user=request.user,
            is_mutual=True,
            liked_user__isnull=False,
        ).select_related("liked_user")

        result = []
        for like in likes:
            result.append(
                {
                    "id": like.id,
                    "is_mutual": like.is_mutual,
                    "created_at": like.created_at,
                    "user": _user_dict(like.liked_user),
                }
            )
        return Response(result)
