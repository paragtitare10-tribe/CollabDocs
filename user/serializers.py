import re

from rest_framework import serializers
from rest_framework.exceptions import APIException
from rest_framework import status

from .models import User


class DuplicateEmailError(APIException):
	status_code = status.HTTP_409_CONFLICT
	default_detail = "A user with this email already exists."
	default_code = "email_already_exists"


class UserSerializer(serializers.ModelSerializer):
	email = serializers.EmailField()

	class Meta:
		model = User
		fields = "__all__"

	def validate_email(self, value):
		# Enforce a well-formed address with a dotted domain.
		pattern = r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?)+$"
		if not re.fullmatch(pattern, value):
			raise serializers.ValidationError("Enter a valid email address.")
		if User.objects.filter(email=value).exists():
			raise DuplicateEmailError()
		return value

	def validate(self, attrs):
		for field, value in attrs.items():
			if isinstance(value, str) and not value.strip():
				raise serializers.ValidationError({field: "This field cannot be blank."})
		return attrs
