from django.urls import reverse
from rest_framework.test import APITestCase

from comment.models import Comment
from document.models import Document
from user.models import User
from .models import Workspace, WorkspaceMember


class WorkspaceCreateApiTests(APITestCase):
	def test_create_workspace_makes_owner_an_admin_member(self):
		owner = User.objects.create(
			first_name="Test",
			last_name="Owner",
			email="owner@example.com",
			phone="1234567890",
		)

		response = self.client.post(
			reverse("workspace-list"),
			{"name": "Team Space", "owner": str(owner.id)},
			format="json",
		)

		self.assertEqual(response.status_code, 201)
		workspace = Workspace.objects.get(id=response.data["id"])
		self.assertEqual(workspace.owner, owner)
		self.assertTrue(
			WorkspaceMember.objects.filter(
				workspace=workspace,
				user=owner,
				role=WorkspaceMember.Role.ADMIN,
			).exists()
		)

	def test_add_member_to_workspace(self):
		owner = User.objects.create(
			first_name="Workspace",
			last_name="Owner",
			email="workspace-owner@example.com",
			phone="1234567890",
		)
		member_user = User.objects.create(
			first_name="Workspace",
			last_name="Member",
			email="workspace-member@example.com",
			phone="0987654321",
		)
		workspace = Workspace.objects.create(name="Team Space", owner=owner)

		response = self.client.post(
			reverse("workspace-add-member", kwargs={"pk": workspace.pk}),
			{"user": str(member_user.id)},
			format="json",
		)

		self.assertEqual(response.status_code, 201)
		self.assertEqual(response.data["role"], WorkspaceMember.Role.MEMBER)
		self.assertTrue(
			WorkspaceMember.objects.filter(
				workspace=workspace,
				user=member_user,
				role=WorkspaceMember.Role.MEMBER,
			).exists()
		)

	def test_get_workspace_includes_member_count(self):
		owner = User.objects.create(
			first_name="Count",
			last_name="Owner",
			email="count-owner@example.com",
			phone="1234567890",
		)
		member_user = User.objects.create(
			first_name="Count",
			last_name="Member",
			email="count-member@example.com",
			phone="0987654321",
		)
		workspace = Workspace.objects.create(name="Team Space", owner=owner)
		WorkspaceMember.objects.create(
			workspace=workspace,
			user=owner,
			role=WorkspaceMember.Role.ADMIN,
		)
		WorkspaceMember.objects.create(
			workspace=workspace,
			user=member_user,
			role=WorkspaceMember.Role.MEMBER,
		)

		response = self.client.get(
			reverse("workspace-detail", kwargs={"pk": workspace.pk})
		)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data["member_count"], 2)

	def test_get_workspace_members_returns_member_roles(self):
		owner = User.objects.create(
			first_name="Members",
			last_name="Owner",
			email="members-owner@example.com",
			phone="1234567890",
		)
		member_user = User.objects.create(
			first_name="Members",
			last_name="Member",
			email="members-member@example.com",
			phone="0987654321",
		)
		workspace = Workspace.objects.create(name="Team Space", owner=owner)
		WorkspaceMember.objects.create(
			workspace=workspace,
			user=owner,
			role=WorkspaceMember.Role.ADMIN,
		)
		WorkspaceMember.objects.create(
			workspace=workspace,
			user=member_user,
			role=WorkspaceMember.Role.MEMBER,
		)

		response = self.client.get(
			reverse("workspace-add-member", kwargs={"pk": workspace.pk})
		)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(len(response.data), 2)
		self.assertEqual(
			{member["role"] for member in response.data},
			{WorkspaceMember.Role.ADMIN, WorkspaceMember.Role.MEMBER},
		)

	def test_workspace_summary_returns_document_member_and_comment_counts(self):
		owner = User.objects.create(
			first_name="Summary",
			last_name="Owner",
			email="summary-owner@example.com",
			phone="1234567890",
		)
		workspace = Workspace.objects.create(name="Team Space", owner=owner)
		WorkspaceMember.objects.create(
			workspace=workspace,
			user=owner,
			role=WorkspaceMember.Role.ADMIN,
		)
		first_document = Document.objects.create(
			title="First document",
			content="Content",
			workspace=workspace,
			created_by=owner,
		)
		Document.objects.create(
			title="Second document",
			content="More content",
			workspace=workspace,
			created_by=owner,
		)
		Comment.objects.create(
			document=first_document,
			author=owner,
			content="First comment",
		)
		Comment.objects.create(
			document=first_document,
			author=owner,
			content="Second comment",
		)

		response = self.client.get(
			reverse("workspace-summary", kwargs={"pk": workspace.pk})
		)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data["document_count"], 2)
		self.assertEqual(response.data["member_count"], 1)
		self.assertEqual(response.data["comment_count"], 2)
