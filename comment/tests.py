from django.urls import reverse
from rest_framework.test import APITestCase

from document.models import Document
from user.models import User
from workspace.models import Workspace

from .models import Comment


class CommentCreateApiTests(APITestCase):
	def setUp(self):
		self.author = User.objects.create(
			first_name="Comment",
			last_name="Author",
			email="comment-author@example.com",
			phone="1234567890",
		)
		self.workspace = Workspace.objects.create(
			name="Comment Space",
			owner=self.author,
		)
		self.document = Document.objects.create(
			title="Commented Notes",
			content="Document content",
			workspace=self.workspace,
			created_by=self.author,
		)

	def test_post_creates_top_level_comment_and_reply(self):
		top_level_response = self.client.post(
			reverse("comment-list"),
			{
				"document": str(self.document.id),
				"author": str(self.author.id),
				"content": "Top-level comment",
			},
			format="json",
		)

		self.assertEqual(top_level_response.status_code, 201)
		self.assertIsNone(top_level_response.data["parent"])
		top_level_comment = Comment.objects.get(id=top_level_response.data["id"])

		reply_response = self.client.post(
			reverse("comment-list"),
			{
				"document": str(self.document.id),
				"author": str(self.author.id),
				"content": "Reply",
				"parent": str(top_level_comment.id),
			},
			format="json",
		)

		self.assertEqual(reply_response.status_code, 201)
		self.assertEqual(reply_response.data["parent"], top_level_comment.id)
		self.assertEqual(Comment.objects.count(), 2)

	def test_post_rejects_parent_from_another_document(self):
		parent = Comment.objects.create(
			document=self.document,
			author=self.author,
			content="Parent comment",
		)
		other_document = Document.objects.create(
			title="Other Notes",
			content="Other content",
			workspace=self.workspace,
			created_by=self.author,
		)

		response = self.client.post(
			reverse("comment-list"),
			{
				"document": str(other_document.id),
				"author": str(self.author.id),
				"content": "Invalid cross-document reply",
				"parent": str(parent.id),
			},
			format="json",
		)

		self.assertEqual(response.status_code, 400)
		self.assertEqual(Comment.objects.count(), 1)

	def test_get_lists_document_comments_as_threads(self):
		root_comment = Comment.objects.create(
			document=self.document,
			author=self.author,
			content="Root comment",
		)
		reply = Comment.objects.create(
			document=self.document,
			author=self.author,
			content="Reply",
			parent=root_comment,
		)
		grandchild_reply = Comment.objects.create(
			document=self.document,
			author=self.author,
			content="Nested reply",
			parent=reply,
		)
		other_document = Document.objects.create(
			title="Other Notes",
			content="Other content",
			workspace=self.workspace,
			created_by=self.author,
		)
		Comment.objects.create(
			document=other_document,
			author=self.author,
			content="Other document comment",
		)

		response = self.client.get(
			reverse("comment-list"), {"document": str(self.document.id)}
		)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(len(response.data), 1)
		self.assertEqual(response.data[0]["id"], str(root_comment.id))
		self.assertEqual(response.data[0]["content"], "Root comment")
		self.assertEqual(response.data[0]["replies"][0]["id"], str(reply.id))
		self.assertEqual(
			response.data[0]["replies"][0]["replies"][0]["id"],
			str(grandchild_reply.id),
		)

	def test_get_requires_document_query_parameter(self):
		response = self.client.get(reverse("comment-list"))

		self.assertEqual(response.status_code, 400)
		self.assertIn("document", response.data)
