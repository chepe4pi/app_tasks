from .serializers import TaskItemSerializer, TaskRecordSerializer
from django.db.models import Sum, Count
from rest_framework import viewsets, permissions
from datetime import datetime
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import TaskRecord, TaskItem, UserSummary
from tasks.tasks import update_total_time

import logging
logger = logging.getLogger(__name__)


class TaskItemViewSet(viewsets.ModelViewSet):
    queryset = TaskItem.objects.all()
    serializer_class = TaskItemSerializer


class TaskRecordViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = TaskRecord.objects.all()
    serializer_class = TaskRecordSerializer

    def list(self, request, *args, **kwargs):
        logger.debug('test123 info')

        self.request.user.abc
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        return TaskRecord.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SummaryViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def daily(self, request):
        date_str = request.query_params.get('date', datetime.now().strftime('%Y-%m-%d'))
        date = datetime.strptime(date_str, '%Y-%m-%d').date()

        records = TaskRecord.objects.filter(user=request.user, date_completed=date)

        summary, created = UserSummary.objects.get_or_create(user=request.user)

        if summary.total_time:
            total_time = summary.total_time
        else:
            # Aggregation for total time spent
            total_time = records.aggregate(total_time=Sum('time_spent'))['total_time'] or 0

            update_total_time.delay(total_time, summary.id)

        # Aggregation for priority count
        priority_counts = records.values('task__priority').annotate(count=Count('task__priority'))

        # Transform priority_counts to a dictionary
        priorities = {
            'low': 0,
            'medium': 0,
            'high': 0
        }

        for item in priority_counts:
            priorities[item['task__priority']] = item['count']

        summary = {
            'total_tasks': records.count(),
            'total_time_spent': total_time,
            'priorities': priorities,
        }

        return Response(summary)
