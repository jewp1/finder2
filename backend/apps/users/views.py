import logging

from django.contrib.auth import get_user_model
from django.db import connection
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.serializers import LoginSerializer, RegisterSerializer, UserSerializer

User = get_user_model()
logger = logging.getLogger(__name__)


def _get_token(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            logger.info("User registered: id=%s email=%s", user.id, user.email)
            return Response(
                {
                    "user": UserSerializer(user).data,
                    "access_token": _get_token(user),
                    "token_type": "bearer",
                },
                status=status.HTTP_201_CREATED,
            )
        logger.warning("Registration failed: %s", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        identifier = serializer.validated_data["username"]
        password = serializer.validated_data["password"]

        user = User.objects.filter(email=identifier).first()
        if not user:
            user = User.objects.filter(username=identifier).first()

        if not user or not user.check_password(password):
            logger.warning("Failed login attempt for identifier=%s", identifier)
            return Response(
                {"detail": "Incorrect username/email or password"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        if not user.is_active:
            logger.warning("Login attempt for inactive user: id=%s", user.id)
            return Response({"detail": "Inactive user"}, status=status.HTTP_400_BAD_REQUEST)

        logger.info("User logged in: id=%s email=%s", user.id, user.email)
        return Response(
            {
                "user": UserSerializer(user).data,
                "access_token": _get_token(user),
                "token_type": "bearer",
            }
        )


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"user": UserSerializer(request.user).data})


class UserListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        users = User.objects.all()
        return Response(UserSerializer(users, many=True).data)


class RootView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"message": "Welcome to Project Finder API", "version": "2.0.0"})


class HealthView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            connection.ensure_connection()
            db_status = "connected"
        except Exception:
            db_status = "disconnected"
        return Response(
            {
                "status": "healthy" if db_status == "connected" else "unhealthy",
                "database": db_status,
                "api": "running",
            }
        )
