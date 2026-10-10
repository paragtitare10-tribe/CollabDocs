from rest_framework.viewsets import ModelViewSet

from .models import Comment
from .serializers import CommentListQuerySerializer, CommentSerializer


class CommentViewSet(ModelViewSet):
	queryset = Comment.objects.select_related("document", "author", "parent")
	serializer_class = CommentSerializer
	http_method_names = ["post", "get"]

	def get_queryset(self):
		if self.action == "list":
			query_serializer = CommentListQuerySerializer(data=self.request.query_params)
			query_serializer.is_valid(raise_exception=True)
			return (
				Comment.objects.filter(
					document_id=query_serializer.validated_data["document"],
					parent__isnull=True,
				)
				.select_related("document", "author")
				.order_by("created_at")
			)
		return super().get_queryset()

