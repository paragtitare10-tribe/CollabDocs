from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import AuditLog
from .serializers import AuditLogFilterSerializer, AuditLogSerializer


class AuditLogViewSet(ReadOnlyModelViewSet):
	queryset = AuditLog.objects.select_related("actor")
	serializer_class = AuditLogSerializer

	def get_queryset(self):
		filter_serializer = AuditLogFilterSerializer(data=self.request.query_params)
		filter_serializer.is_valid(raise_exception=True)
		filters = filter_serializer.validated_data
		return super().get_queryset().filter(
			actor_id=filters["actor_id"],
			timestamp__date__range=(filters["start_date"], filters["end_date"]),
		).order_by("-timestamp")