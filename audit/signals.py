from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from document.models import Document

from .models import AuditLog


@receiver(pre_save, sender=Document)
def capture_document_creation_state(sender, instance, **kwargs):
	instance._was_adding_before_save = instance._state.adding


@receiver(post_save, sender=Document)
def log_document_save(sender, instance, **kwargs):
	was_adding = getattr(instance, "_was_adding_before_save", False)
	action = "Document created" if was_adding else "Document updated"
	AuditLog.objects.create(
		action=action,
		actor=instance.created_by,
		model_name="Document",
		object_id=instance.pk,
	)