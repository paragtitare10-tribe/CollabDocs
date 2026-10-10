import uuid

from django.db import models


class Tag(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	name = models.CharField(max_length=100, unique=True)
	documents = models.ManyToManyField(
		"document.Document",
		related_name="tags",
		blank=True,
	)

	def __str__(self):
		return self.name