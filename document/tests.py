from unittest.mock import patch

from django.db import IntegrityError
from django.urls import reverse
from rest_framework.test import APITestCase

from audit.models import AuditLog
from comment.models import Comment
from tags.models import Tag
from user.models import User
from workspace.models import Workspace

from .models import Document, DocumentVersion


class DocumentCreateApiTests(APITestCase):
	def test_create_document_creates_initial_version(self):
		owner = User.objects.create(
			first_name="Document",
			last_name="Owner",
			email="document-owner@example.com",
			phone="1234567890",
		)
		workspace = Workspace.objects.create(name="Team Space", owner=owner)

		response = self.client.post(
			reverse("document-list"),
			{
				"title": "Project Notes",
				"content": "Initial document content",
				"workspace": str(workspace.id),
				"created_by": str(owner.id),
			},
			format="json",
		)

		self.assertEqual(response.status_code, 201)
		self.assertEqual(response.data["version_number"], 1)
		document = Document.objects.get(id=response.data["id"])
		version = DocumentVersion.objects.get(document=document)
		self.assertEqual(version.version_number, 1)
		self.assertEqual(version.content, document.content)
		self.assertEqual(version.saved_by, owner)

	def test_create_rolls_back_document_and_audit_log_if_version_creation_fails(self):
		owner = User.objects.create(
			first_name="Atomic",
			last_name="Owner",
			email="atomic-owner@example.com",
			phone="1234567893",
		)
		workspace = Workspace.objects.create(name="Atomic Space", owner=owner)
		audit_log_count = AuditLog.objects.count()
		version_count = DocumentVersion.objects.count()

		with patch(
			"document.serializers.DocumentVersion.objects.create",
			side_effect=IntegrityError("Simulated version insert failure"),
		):
			with self.assertRaises(IntegrityError):
				self.client.post(
					reverse("document-list"),
					{
						"title": "Atomic document",
						"content": "This should roll back",
						"workspace": str(workspace.id),
						"created_by": str(owner.id),
					},
					format="json",
				)

		self.assertFalse(Document.objects.filter(title="Atomic document").exists())
		self.assertEqual(DocumentVersion.objects.count(), version_count)
		self.assertEqual(AuditLog.objects.count(), audit_log_count)

	def test_put_document_updates_content_and_creates_new_version(self):
		owner = User.objects.create(
			first_name="Update",
			last_name="Owner",
			email="update-owner@example.com",
			phone="1234567890",
		)
		workspace = Workspace.objects.create(name="Update Space", owner=owner)
		document = Document.objects.create(
			title="Project Notes",
			content="Original content",
			workspace=workspace,
			created_by=owner,
		)
		DocumentVersion.objects.create(
			document=document,
			version_number=1,
			content=document.content,
			saved_by=owner,
		)

		response = self.client.put(
			reverse("document-detail", args=[document.id]),
			{
				"title": document.title,
				"content": "Updated content",
				"workspace": str(workspace.id),
				"created_by": str(owner.id),
				"status": document.status,
			},
			format="json",
		)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data["version_number"], 2)
		document.refresh_from_db()
		self.assertEqual(document.content, "Updated content")
		self.assertEqual(document.versions.count(), 2)
		new_version = document.versions.get(version_number=2)
		self.assertEqual(new_version.content, "Updated content")
		self.assertEqual(new_version.saved_by, owner)

	def test_document_versions_endpoint_returns_versions_in_order(self):
		owner = User.objects.create(
			first_name="Version",
			last_name="Owner",
			email="version-owner@example.com",
			phone="1234567890",
		)
		workspace = Workspace.objects.create(name="Version Space", owner=owner)
		document = Document.objects.create(
			title="Versioned Notes",
			content="Current content",
			workspace=workspace,
			created_by=owner,
		)
		for version_number in (3, 1, 2):
			DocumentVersion.objects.create(
				document=document,
				version_number=version_number,
				content=f"Content for version {version_number}",
				saved_by=owner,
			)

		response = self.client.get(
			reverse("document-versions", args=[document.id])
		)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(
			[version["version_number"] for version in response.data], [1, 2, 3]
		)
		self.assertEqual(
			[version["content"] for version in response.data],
			["Content for version 1", "Content for version 2", "Content for version 3"],
		)

	def test_document_stats_returns_version_comment_and_contributor_counts(self):
		owner = User.objects.create(
			first_name="Stats",
			last_name="Owner",
			email="stats-owner@example.com",
			phone="1234567890",
		)
		contributor = User.objects.create(
			first_name="Stats",
			last_name="Contributor",
			email="stats-contributor@example.com",
			phone="1234567891",
		)
		workspace = Workspace.objects.create(name="Stats Space", owner=owner)
		document = Document.objects.create(
			title="Statistics Notes",
			content="Current content",
			workspace=workspace,
			created_by=owner,
		)
		DocumentVersion.objects.create(
			document=document,
			version_number=1,
			content="Initial content",
			saved_by=owner,
		)
		DocumentVersion.objects.create(
			document=document,
			version_number=2,
			content="Updated content",
			saved_by=contributor,
		)
		Comment.objects.create(
			document=document,
			author=contributor,
			content="Looks good",
		)
		Comment.objects.create(
			document=document,
			author=owner,
			content="Thanks",
		)

		response = self.client.get(reverse("document-stats", args=[document.id]))

		self.assertEqual(response.status_code, 200)
		self.assertEqual(
			response.data,
			{"version_count": 2, "comment_count": 2, "contributor_count": 2},
		)

	def test_post_document_tags_adds_multiple_tags_without_removing_existing(self):
		owner = User.objects.create(
			first_name="Tag",
			last_name="Owner",
			email="tag-owner@example.com",
			phone="1234567890",
		)
		workspace = Workspace.objects.create(name="Tag Space", owner=owner)
		document = Document.objects.create(
			title="Tagged Notes",
			content="Document content",
			workspace=workspace,
			created_by=owner,
		)
		existing_tag = Tag.objects.create(name="Existing")
		planning_tag = Tag.objects.create(name="Planning")
		document.tags.add(existing_tag)

		response = self.client.post(
			reverse("document-tags", args=[document.id]),
			{"tags": ["Planning", "Review"]},
			format="json",
		)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(
			response.data,
			{
				"document_id": str(document.id),
				"tags": ["Existing", "Planning", "Review"],
			},
		)
		self.assertSetEqual(
			set(document.tags.values_list("id", flat=True)),
			{existing_tag.id, planning_tag.id, Tag.objects.get(name="Review").id},
		)

	def test_list_documents_filters_by_workspace_status_tag_and_title(self):
		owner = User.objects.create(
			first_name="Filter",
			last_name="Owner",
			email="filter-owner@example.com",
			phone="1234567890",
		)
		workspace = Workspace.objects.create(name="Team Space", owner=owner)
		other_workspace = Workspace.objects.create(name="Other Space", owner=owner)
		matching_document = Document.objects.create(
			title="Roadmap planning",
			content="First content",
			workspace=workspace,
			created_by=owner,
			status=Document.Status.PUBLISHED,
		)
		wrong_status_document = Document.objects.create(
			title="Roadmap draft",
			content="Second content",
			workspace=workspace,
			created_by=owner,
			status=Document.Status.DRAFT,
		)
		wrong_title_document = Document.objects.create(
			title="Release notes",
			content="Third content",
			workspace=workspace,
			created_by=owner,
			status=Document.Status.PUBLISHED,
		)
		wrong_workspace_document = Document.objects.create(
			title="Roadmap elsewhere",
			content="Fourth content",
			workspace=other_workspace,
			created_by=owner,
			status=Document.Status.PUBLISHED,
		)
		planning_tag = Tag.objects.create(name="Planning")
		planning_tag.documents.add(
			matching_document,
			wrong_status_document,
			wrong_title_document,
			wrong_workspace_document,
		)

		response = self.client.get(
			reverse("document-list"),
			{
				"workspace": str(workspace.id),
				"status": Document.Status.PUBLISHED,
				"tag": "planning",
				"search": "Roadmap",
			},
		)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(len(response.data), 1)
		self.assertEqual(response.data[0]["id"], str(matching_document.id))

	def test_list_documents_searches_title_or_content_case_insensitively(self):
		owner = User.objects.create(
			first_name="Search",
			last_name="Owner",
			email="search-owner@example.com",
			phone="1234567890",
		)
		workspace = Workspace.objects.create(name="Search Space", owner=owner)
		title_match = Document.objects.create(
			title="Release KEYWORD notes",
			content="Unrelated content",
			workspace=workspace,
			created_by=owner,
		)
		content_match = Document.objects.create(
			title="Meeting notes",
			content="Contains keyword in the body",
			workspace=workspace,
			created_by=owner,
		)
		Document.objects.create(
			title="Unrelated document",
			content="No match here",
			workspace=workspace,
			created_by=owner,
		)

		response = self.client.get(reverse("document-list"), {"search": "keyword"})

		self.assertEqual(response.status_code, 200)
		self.assertCountEqual(
			[document["id"] for document in response.data],
			[str(title_match.id), str(content_match.id)],
		)
