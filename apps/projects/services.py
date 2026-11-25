from django.db import transaction
from django.db.models import Max

from .models import Project, ProjectVersion

DEFAULT_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Untitled Project</title>
  <link rel="stylesheet" href="styles.css" />
</head>
<body>
  <main class="container">
    <h1>Welcome to PixelForge AI</h1>
    <p>Start editing or generate a layout using AI.</p>
  </main>
  <script src="script.js"></script>
</body>
</html>
"""

DEFAULT_CSS = """* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: system-ui, -apple-system, sans-serif;
  line-height: 1.6;
  padding: 2rem;
}
"""

DEFAULT_JS = """console.log('PixelForge AI project loaded');\n"""


class ProjectService:
    @staticmethod
    @transaction.atomic
    def create_project(
        user,
        name,
        description="",
        html_content=None,
        css_content=None,
        js_content=None,
        prompt_used=None,
    ):
        project = Project.objects.create(
            user=user,
            name=name,
            description=description,
        )
        ProjectVersion.objects.create(
            project=project,
            version_number=1,
            html_content=html_content if html_content is not None else DEFAULT_HTML,
            css_content=css_content if css_content is not None else DEFAULT_CSS,
            js_content=js_content if js_content is not None else DEFAULT_JS,
            prompt_used=prompt_used or "Initial project version",
        )
        return project

    @staticmethod
    @transaction.atomic
    def save_new_version(
        project, html_content, css_content, js_content, prompt_used="Manual save"
    ):
        latest = project.versions.aggregate(max_v=Max("version_number"))["max_v"] or 0
        version = ProjectVersion.objects.create(
            project=project,
            version_number=latest + 1,
            html_content=html_content,
            css_content=css_content,
            js_content=js_content,
            prompt_used=prompt_used,
        )
        project.save(update_fields=["updated_at"])
        return version

    @staticmethod
    @transaction.atomic
    def restore_version(project, target_version):
        return ProjectService.save_new_version(
            project=project,
            html_content=target_version.html_content,
            css_content=target_version.css_content,
            js_content=target_version.js_content,
            prompt_used=f"Restored from v{target_version.version_number}",
        )
