from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase

from .models import User


class DuplicateEmailApiTests(APITestCase):
	def test_duplicate_email_returns_conflict_with_detail(self):
		User.objects.create(
			first_name="Existing",
			last_name="User",
			email="existing@example.com",
			phone="1111111111",
		)

		response = self.client.post(
			reverse("user-list"),
			{
				"first_name": "New",
				"last_name": "User",
				"email": "existing@example.com",
				"phone": "2222222222",
			},
			format="json",
		)

		self.assertEqual(response.status_code, 409)
		self.assertEqual(
			response.data["detail"], "A user with this email already exists."
		)
