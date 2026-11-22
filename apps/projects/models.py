from django.db import models

# Create your models here.
import uuid
from django.db import models
from django.contrib.auth.models import User

class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-updated_at']

class ProjectVersion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='versions')
    version_number = models.PositiveIntegerField()
    html_content = models.TextField(blank=True)
    css_content = models.TextField(blank=True)
    js_content = models.TextField(blank=True)
    prompt_used = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-version_number']
        unique_together = ('project', 'version_number')

    def __str__(self):
        return f"{self.project.name} - v{self.version_number}"