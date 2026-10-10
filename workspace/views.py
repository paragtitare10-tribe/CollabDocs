from django.db.models import Count
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from comment.models import Comment
from .models import Workspace
from .serializers import WorkspaceMemberSerializer, WorkspaceSerializer


class WorkspaceViewSet(ModelViewSet):
	queryset = Workspace.objects.annotate(member_count=Count("members"))
	serializer_class = WorkspaceSerializer
	http_method_names = ["post", "get"]

	@action(detail=True, methods=["get"], url_path="summary")
	def summary(self, request, pk=None):
		workspace = self.get_object()
		return Response(
			{
				"workspace_id": str(workspace.id),
				"document_count": workspace.documents.count(),
				"member_count": workspace.members.count(),
				"comment_count": Comment.objects.filter(
					document__workspace=workspace
				).count(),
			}
		)

	@action(detail=True, methods=["get", "post"], url_path="members")
	def add_member(self, request, pk=None):
		workspace = self.get_object()
		if request.method == "GET":
			members = workspace.members.select_related("user").all()
			serializer = WorkspaceMemberSerializer(members, many=True)
			return Response(serializer.data)

		serializer = WorkspaceMemberSerializer(
			data=request.data,
			context={"workspace": workspace},
		)
		serializer.is_valid(raise_exception=True)
		member = serializer.save(workspace=workspace)
		return Response(
			WorkspaceMemberSerializer(member).data,
			status=status.HTTP_201_CREATED,
		)
