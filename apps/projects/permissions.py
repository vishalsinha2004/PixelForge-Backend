from rest_framework import permissions


class IsProjectOwner(permissions.BasePermission):
    """Allow access only to the authenticated user who owns the project."""

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
