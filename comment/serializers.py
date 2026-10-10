from rest_framework import serializers

from .models import Comment


class CommentSerializer(serializers.ModelSerializer):
	replies = serializers.SerializerMethodField()

	class Meta:
		model = Comment
		fields = (
			"id",
			"document",
			"author",
			"content",
			"parent",
			"created_at",
			"replies",
		)
		read_only_fields = ("id", "created_at", "replies")

	def get_replies(self, comment):
		replies = comment.replies.select_related("document", "author", "parent").order_by(
			"created_at"
		)
		return CommentSerializer(replies, many=True, context=self.context).data

	def validate(self, attrs):
		parent = attrs.get("parent")
		document = attrs.get("document")
		if parent is not None and parent.document_id != document.id:
			raise serializers.ValidationError(
				{"parent": "The parent comment must belong to the same document."}
			)
		return attrs


class CommentListQuerySerializer(serializers.Serializer):
	document = serializers.UUIDField()