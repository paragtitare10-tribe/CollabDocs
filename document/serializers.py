from django.db import transaction
from django.db.models import Max
from rest_framework import serializers

from .models import Document, DocumentVersion


class DocumentVersionSerializer(serializers.ModelSerializer):
	class Meta:
		model = DocumentVersion
		fields = (
			"id",
			"document",
			"version_number",
			"content",
			"saved_by",
			"created_at",
		)
		read_only_fields = fields


class DocumentTagsInputSerializer(serializers.Serializer):
	tags = serializers.ListField(
		child=serializers.CharField(max_length=100),
		allow_empty=False,
	)


class DocumentSerializer(serializers.ModelSerializer):
	version_number = serializers.SerializerMethodField()

	class Meta:
		model = Document
		fields = (
			"id",
			"title",
			"content",
			"workspace",
			"created_by",
			"status",
			"updated_at",
			"version_number",
		)
		read_only_fields = ("id", "updated_at", "version_number")

	def get_version_number(self, document):
		annotated_version = getattr(document, "current_version_number", None)
		if annotated_version is not None:
			return annotated_version
		return (
			document.versions.order_by("-version_number")
			.values_list("version_number", flat=True)
			.first()
			or 0
		)

	@transaction.atomic
	def create(self, validated_data):
		document = Document.objects.create(**validated_data)
		DocumentVersion.objects.create(
			document=document,
			version_number=1,
			content=document.content,
			saved_by=document.created_by,
		)
		return document

	@transaction.atomic
	def update(self, instance, validated_data):
		Document.objects.select_for_update().get(pk=instance.pk)
		instance = super().update(instance, validated_data)
		latest_version_number = instance.versions.aggregate(
			latest_version_number=Max("version_number")
		)["latest_version_number"] or 0
		version = DocumentVersion.objects.create(
			document=instance,
			version_number=latest_version_number + 1,
			content=instance.content,
			saved_by=instance.created_by,
		)
		instance.current_version_number = version.version_number
		return instance