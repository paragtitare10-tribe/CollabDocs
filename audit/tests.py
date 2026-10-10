from datetime import datetime

from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase

from document.models import Document
from user.models import User
from workspace.models import Workspace

from .models import AuditLog


class AuditLogListApiTests(APITestCase):
	def test_get_filters_audit_logs_by_actor_and_inclusive_date_range(self):
		actor = User.objects.create(
			first_name="Audit",
			last_name="Actor",
			email="audit-actor@example.com",
			phone="1234567890",
		)
		other_actor = User.objects.create(
			first_name="Other",
			last_name="Actor",
			email="other-actor@example.com",
			phone="1234567891",
		)

		def create_log(log_actor, action, timestamp):
			log = AuditLog.objects.create(
				action=action,
				actor=log_actor,
				model_name="Document",
				object_id="12345678-1234-5678-1234-567812345678",
			)
			AuditLog.objects.filter(pk=log.pk).update(
				timestamp=timezone.make_aware(datetime.fromisoformat(timestamp))
			)
			return log

		start_log = create_log(actor, "start day", "2026-03-10T00:05:00")
		end_log = create_log(actor, "end day", "2026-03-12T23:59:00")
		create_log(actor, "before range", "2026-03-09T23:59:00")
		create_log(other_actor, "other actor", "2026-03-11T12:00:00")

		response = self.client.get(
			reverse("audit-log-list"),
			{
				"actor_id": str(actor.id),
				"start_date": "2026-03-10",
				"end_date": "2026-03-12",
			},
		)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(
			[entry["id"] for entry in response.data],
			[str(end_log.id), str(start_log.id)],
		)


class DocumentAuditSignalTests(APITestCase):
	def test_document_create_and_update_write_audit_logs(self):
		actor = User.objects.create(
			first_name="Signal",
			last_name="Actor",
			email="signal-actor@example.com",
			phone="1234567892",
		)
		workspace = Workspace.objects.create(name="Signal Space", owner=actor)
		document = Document.objects.create(
			title="Signal Notes",
			content="Original content",
			workspace=workspace,
			created_by=actor,
		)
		created_log = AuditLog.objects.get(object_id=document.id)

		document.title = "Updated Signal Notes"
		document.save()
		updated_log = AuditLog.objects.filter(object_id=document.id).latest("timestamp")

		self.assertEqual(
			list(
				AuditLog.objects.filter(object_id=document.id)
					.order_by("timestamp")
				.values_list("action", flat=True)
			),
			["Document created", "Document updated"],
		)
		self.assertEqual(created_log.actor, actor)
		self.assertEqual(updated_log.actor, actor)
		self.assertEqual(created_log.model_name, "Document")