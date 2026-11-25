from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.accounts.views import CurrentUserView, HealthCheckView
from apps.projects.views import ProjectViewSet

router = DefaultRouter()
router.register(r"projects", ProjectViewSet, basename="project")

urlpatterns = [
    path("health/", HealthCheckView.as_view(), name="health-check"),
    path("auth/me/", CurrentUserView.as_view(), name="auth-me"),
    path("", include(router.urls)),
]
