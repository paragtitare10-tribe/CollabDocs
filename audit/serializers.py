from rest_framework import serializers

from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
	class Meta:
		model = AuditLog
		fields = ("id", "action", "actor", "model_name", "object_id", "timestamp")
		read_only_fields = fields


class AuditLogFilterSerializer(serializers.Serializer):
	actor_id = serializers.UUIDField()
	start_date = serializers.DateField()
	end_date = serializers.DateField()

	def validate(self, attrs):
		if attrs["start_date"] > attrs["end_date"]:
			raise serializers.ValidationError(
				{"end_date": "Must be on or after start_date."}
			)
		return attrs