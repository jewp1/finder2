import logging

from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.projects.models import Project
from apps.projects.serializers import ProjectSerializer, ProjectWithOwnerSerializer

logger = logging.getLogger(__name__)


class ProjectListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request):
        qs = Project.objects.select_related("owner").all().order_by("-created_at")
        search = request.query_params.get("search")
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(description__icontains=search))
        skip = int(request.query_params.get("skip", 0))
        limit = int(request.query_params.get("limit", 100))
        qs = qs[skip : skip + limit]
        return Response(ProjectWithOwnerSerializer(qs, many=True).data)

    def post(self, request):
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            project = serializer.save(owner=request.user)
            logger.info("Project created: id=%s owner=%s title=%r", project.id, request.user.id, project.title)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.warning("Project creation failed: user=%s errors=%s", request.user.id, serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProjectDetailView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request, project_id):
        project = get_object_or_404(Project.objects.select_related("owner"), pk=project_id)
        return Response(ProjectWithOwnerSerializer(project).data)

    def put(self, request, project_id):
        project = get_object_or_404(Project, pk=project_id)
        if project.owner != request.user:
            logger.warning("Unauthorized project update: user=%s project=%s", request.user.id, project_id)
            return Response({"detail": "Not enough permissions"}, status=status.HTTP_403_FORBIDDEN)
        serializer = ProjectSerializer(project, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            logger.info("Project updated: id=%s user=%s", project_id, request.user.id)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, project_id):
        project = get_object_or_404(Project, pk=project_id)
        if project.owner != request.user:
            logger.warning("Unauthorized project delete: user=%s project=%s", request.user.id, project_id)
            return Response({"detail": "Not enough permissions"}, status=status.HTTP_403_FORBIDDEN)
        project.delete()
        logger.info("Project deleted: id=%s user=%s", project_id, request.user.id)
        return Response({"message": "Project deleted successfully"})
