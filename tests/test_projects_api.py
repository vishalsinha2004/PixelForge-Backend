import jwt
import pytest
from django.contrib.auth.models import User
from django.test import override_settings
from rest_framework.test import APIClient

TEST_JWT_SECRET = "test-supabase-jwt-secret-key-at-least-32-chars"


@pytest.mark.django_db
def test_health_endpoint_is_public():
    client = APIClient()
    response = client.get("/api/v1/health/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.django_db
@override_settings(SUPABASE_JWT_SECRET=TEST_JWT_SECRET)
def test_supabase_jwt_authentication():
    token = jwt.encode(
        {"sub": "supabase-user-uuid-123", "aud": "authenticated"},
        TEST_JWT_SECRET,
        algorithm="HS256",
    )
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    response = client.get("/api/v1/auth/me/")
    assert response.status_code == 200
    assert response.json()["id"] == "supabase-user-uuid-123"


@pytest.mark.django_db
def test_project_crud_and_version_restore():
    user = User.objects.create_user(username="user-a")
    other_user = User.objects.create_user(username="user-b")

    client = APIClient()
    client.force_authenticate(user=user)

    # Create project (automatically creates v1)
    create_res = client.post(
        "/api/v1/projects/",
        {"name": "Landing Page", "description": "SaaS site"},
        format="json",
    )
    assert create_res.status_code == 201
    project_id = create_res.json()["id"]
    v1_id = create_res.json()["latest_version"]["id"]
    assert create_res.json()["version_count"] == 1

    # Save v2
    save_res = client.post(
        f"/api/v1/projects/{project_id}/save/",
        {
            "html_content": "<h1>Version 2</h1>",
            "css_content": "h1 { color: cyan; }",
            "js_content": "console.log('v2');",
            "prompt_used": "Updated heading",
        },
        format="json",
    )
    assert save_res.status_code == 201
    assert save_res.json()["version_number"] == 2

    # Restore v1 -> creates v3 with v1 content
    restore_res = client.post(
        f"/api/v1/projects/{project_id}/versions/{v1_id}/restore/",
        format="json",
    )
    assert restore_res.status_code == 201
    assert restore_res.json()["version_number"] == 3
    assert "Welcome to PixelForge AI" in restore_res.json()["html_content"]

    # Isolation check: User B must not see User A's project
    other_client = APIClient()
    other_client.force_authenticate(user=other_user)
    forbidden_res = other_client.get(f"/api/v1/projects/{project_id}/")
    assert forbidden_res.status_code == 404
