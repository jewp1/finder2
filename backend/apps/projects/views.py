from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db.models import Q
from django.shortcuts import get_object_or_404

from apps.projects.models import Project
from apps.projects.serializers import ProjectSerializer, ProjectWithOwnerSerializer


class ProjectListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request):
        qs = Project.objects.select_related('owner').all().order_by('-created_at')
        search = request.query_params.get('search')
        if search:
            qs = qs.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )
        skip = int(request.query_params.get('skip', 0))
        limit = int(request.query_params.get('limit', 100))
        qs = qs[skip:skip + limit]
        return Response(ProjectWithOwnerSerializer(qs, many=True).data)

    def post(self, request):
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProjectDetailView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request, project_id):
        project = get_object_or_404(Project.objects.select_related('owner'), pk=project_id)
        return Response(ProjectWithOwnerSerializer(project).data)

    def put(self, request, project_id):
        project = get_object_or_404(Project, pk=project_id)
        if project.owner != request.user:
            return Response({'detail': 'Not enough permissions'}, status=status.HTTP_403_FORBIDDEN)
        serializer = ProjectSerializer(project, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, project_id):
        project = get_object_or_404(Project, pk=project_id)
        if project.owner != request.user:
            return Response({'detail': 'Not enough permissions'}, status=status.HTTP_403_FORBIDDEN)
        project.delete()
        return Response({'message': 'Project deleted successfully'})
