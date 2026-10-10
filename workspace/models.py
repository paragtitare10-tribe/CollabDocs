import uuid

from django.db import models

class Workspace(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    owner = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='workspaces')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name + " (Owner: " + str(self.owner) + ") - Active: " + str(self.is_active) + " - Created At: " + str(self.created_at)

class WorkspaceMember(models.Model):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        MEMBER = 'member', 'Member'
        VIEWER = 'viewer', 'Viewer'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='workspace_memberships')
    role = models.CharField(max_length=50, choices=Role.choices)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['workspace', 'user'],
                name='unique_workspace_member',
            ),
        ]

    def __str__(self):
        return f"{self.user} in {self.workspace} as {self.role} - Joined At: {self.joined_at}"