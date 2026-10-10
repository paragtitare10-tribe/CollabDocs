from django.urls import reverse
from rest_framework.test import APITestCase

from .models import Tag


class TagCreateApiTests(APITestCase):
	def test_post_creates_tag(self):
		response = self.client.post(
			reverse("tag-list"), {"name": "Planning"}, format="json"
		)

		self.assertEqual(response.status_code, 201)
		self.assertEqual(response.data["name"], "Planning")
		self.assertTrue(Tag.objects.filter(name="Planning").exists())

	def test_post_rejects_duplicate_tag_name(self):
		Tag.objects.create(name="Planning")

		response = self.client.post(
			reverse("tag-list"), {"name": "Planning"}, format="json"
		)

		self.assertEqual(response.status_code, 400)
		self.assertEqual(Tag.objects.count(), 1)