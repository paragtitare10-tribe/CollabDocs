from django.db import transaction
from rest_framework import serializers

from .models import Workspace, WorkspaceMember

class WorkspaceSerializer(serializers.ModelSerializer):
	member_count = serializers.SerializerMethodField()

	class Meta:
		model = Workspace
		fields = ("id", "name", "owner", "is_active", "created_at", "member_count")
		read_only_fields = ("id", "is_active", "created_at")

	def get_member_count(self, workspace):
		annotated_count = getattr(workspace, "member_count", None)
		if annotated_count is not None:
			return annotated_count
		return workspace.members.count()

	@transaction.atomic
	def create(self, validated_data):
		workspace = Workspace.objects.create(**validated_data)
		WorkspaceMember.objects.create(
			workspace=workspace,
			user=workspace.owner,
			role=WorkspaceMember.Role.ADMIN,
		)
		return workspace


class WorkspaceMemberSerializer(serializers.ModelSerializer):
	role = serializers.ChoiceField(
		choices=WorkspaceMember.Role.choices,
		required=False,
		default=WorkspaceMember.Role.MEMBER,
	)

	class Meta:
		model = WorkspaceMember
		fields = ("id", "user", "role", "joined_at")
		read_only_fields = ("id", "joined_at")

	def validate(self, attrs):
		workspace = self.context["workspace"]
		if WorkspaceMember.objects.filter(
			workspace=workspace,
			user=attrs["user"],
		).exists():
			raise serializers.ValidationError(
				{"user": "This user is already a member of this workspace."}
			)
		return attrs