import uuid

from django.db import models


class AuditLog(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	action = models.CharField(max_length=255)
	actor = models.ForeignKey(
		"user.User",
		on_delete=models.SET_NULL,
		null=True,
		related_name="audit_logs",
	)
	model_name = models.CharField(max_length=100)
	object_id = models.UUIDField()
	timestamp = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.action} by {self.actor} on {self.model_name} at {self.timestamp}"