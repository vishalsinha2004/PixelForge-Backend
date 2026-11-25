from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Project, ProjectVersion
from .permissions import IsProjectOwner
from .serializers import (
    ProjectSerializer,
    ProjectVersionSerializer,
    SaveVersionSerializer,
)
from .services import ProjectService


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsProjectOwner]

    def get_queryset(self):
        return Project.objects.filter(user=self.request.user).prefetch_related(
            "versions"
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        project = ProjectService.create_project(
            user=request.user,
            name=serializer.validated_data["name"],
            description=serializer.validated_data.get("description", ""),
        )
        output = self.get_serializer(project)
        return Response(output.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="save")
    def save_code(self, request, pk=None):
        project = self.get_object()
        serializer = SaveVersionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        version = ProjectService.save_new_version(
            project=project,
            html_content=serializer.validated_data["html_content"],
            css_content=serializer.validated_data["css_content"],
            js_content=serializer.validated_data["js_content"],
            prompt_used=serializer.validated_data["prompt_used"],
        )
        return Response(
            ProjectVersionSerializer(version).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["get"], url_path="versions")
    def list_versions(self, request, pk=None):
        project = self.get_object()
        versions = project.versions.all()
        return Response(ProjectVersionSerializer(versions, many=True).data)

    @action(
        detail=True,
        methods=["post"],
        url_path=r"versions/(?P<version_id>[^/.]+)/restore",
    )
    def restore_version(self, request, pk=None, version_id=None):
        project = self.get_object()
        target_version = get_object_or_404(
            ProjectVersion, id=version_id, project=project
        )
        restored = ProjectService.restore_version(project, target_version)
        return Response(
            ProjectVersionSerializer(restored).data,
            status=status.HTTP_201_CREATED,
        )
