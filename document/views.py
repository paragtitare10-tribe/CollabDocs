from django.db import transaction
from django.db.models import Max, Q
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from tags.models import Tag

from .models import Document
from .serializers import (
	DocumentSerializer,
	DocumentTagsInputSerializer,
	DocumentVersionSerializer,
)


class DocumentViewSet(ModelViewSet):
	queryset = Document.objects.annotate(
		current_version_number=Max("versions__version_number")
	)
	serializer_class = DocumentSerializer
	http_method_names = ["get", "post", "put"]

	@action(detail=True, methods=["get"], url_path="versions")
	def versions(self, request, pk=None):
		document = self.get_object()
		versions = document.versions.order_by("version_number")
		serializer = DocumentVersionSerializer(versions, many=True)
		return Response(serializer.data)

	@action(detail=True, methods=["post"], url_path="tags")
	@transaction.atomic
	def tags(self, request, pk=None):
		document = self.get_object()
		serializer = DocumentTagsInputSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)

		tags = [
			Tag.objects.get_or_create(name=name)[0]
			for name in serializer.validated_data["tags"]
		]
		document.tags.add(*tags)
		return Response(
			{
				"document_id": str(document.pk),
				"tags": list(document.tags.order_by("name").values_list("name", flat=True)),
			}
		)

	@action(detail=True, methods=["get"], url_path="stats")
	def stats(self, request, pk=None):
		document = self.get_object()
		contributor_ids = set(
			document.versions.exclude(saved_by_id=None)
			.values_list("saved_by_id", flat=True)
			.distinct()
		)
		contributor_ids.update(
			document.comments.exclude(author_id=None)
			.values_list("author_id", flat=True)
			.distinct()
		)
		if document.created_by_id is not None:
			contributor_ids.add(document.created_by_id)

		return Response(
			{
				"version_count": document.versions.count(),
				"comment_count": document.comments.count(),
				"contributor_count": len(contributor_ids),
			}
		)

	def get_queryset(self):
		queryset = super().get_queryset()
		workspace_id = self.request.query_params.get("workspace")
		status_value = self.request.query_params.get("status")
		tag_name = self.request.query_params.get("tag")
		search_term = self.request.query_params.get("search")

		if workspace_id:
			queryset = queryset.filter(workspace_id=workspace_id)
		if status_value:
			queryset = queryset.filter(status=status_value)
		if tag_name:
			queryset = queryset.filter(tags__name__iexact=tag_name).distinct()
		if search_term:
			queryset = queryset.filter(
				Q(title__icontains=search_term) | Q(content__icontains=search_term)
			)
		return queryset


