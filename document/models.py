import uuid

from django.db import models

class Document(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        PUBLISHED = 'published', 'Published'
        ARCHIVED = 'archived', 'Archived'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    content = models.TextField()
    workspace = models.ForeignKey('workspace.Workspace', on_delete=models.CASCADE, related_name='documents')
    created_by = models.ForeignKey('user.User', on_delete=models.SET_NULL, null=True, related_name='created_documents')
    status = models.CharField(max_length=50, choices=Status.choices, default=Status.DRAFT)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title + " (Workspace: " + str(self.workspace) + ") - Status: " + self.status + " - Updated At: " + str(self.updated_at)


class DocumentVersion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='versions')
    version_number = models.PositiveIntegerField()
    content = models.TextField()
    saved_by = models.ForeignKey('user.User', on_delete=models.SET_NULL, null=True, related_name='saved_versions')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('document', 'version_number')

    def __str__(self):
        return f"Version {self.version_number} of Document {self.document.title} - Created At: {self.created_at}"
