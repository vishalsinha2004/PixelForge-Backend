from rest_framework import serializers

from .models import Project, ProjectVersion


class ProjectVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectVersion
        fields = [
            "id",
            "version_number",
            "html_content",
            "css_content",
            "js_content",
            "prompt_used",
            "created_at",
        ]
        read_only_fields = ["id", "version_number", "created_at"]


class ProjectSerializer(serializers.ModelSerializer):
    latest_version = serializers.SerializerMethodField()
    version_count = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "description",
            "created_at",
            "updated_at",
            "version_count",
            "latest_version",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "version_count",
            "latest_version",
        ]

    def validate_name(self, value):
        cleaned = value.strip()
        if not cleaned:
            raise serializers.ValidationError("Project name cannot be blank.")
        return cleaned

    def get_latest_version(self, obj):
        latest = obj.versions.first()
        return ProjectVersionSerializer(latest).data if latest else None

    def get_version_count(self, obj):
        return obj.versions.count()


class SaveVersionSerializer(serializers.Serializer):
    html_content = serializers.CharField(allow_blank=True, default="")
    css_content = serializers.CharField(allow_blank=True, default="")
    js_content = serializers.CharField(allow_blank=True, default="")
    prompt_used = serializers.CharField(
        allow_blank=True, required=False, default="Manual save"
    )
