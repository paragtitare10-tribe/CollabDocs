import uuid

from django.db import models

class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey('document.Document', on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey('user.User', on_delete=models.SET_NULL, null=True, related_name='authored_comments')
    content = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author} on {self.document}"
