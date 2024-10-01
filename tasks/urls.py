from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskItemViewSet, TaskRecordViewSet, SummaryViewSet

router = DefaultRouter()
router.register(r'task', TaskItemViewSet)
router.register(r'task_record', TaskRecordViewSet)
router.register(r'summary', SummaryViewSet, basename='summary')

urlpatterns = [
    path('api/', include(router.urls)),
]
