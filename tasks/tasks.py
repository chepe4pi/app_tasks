import os

from celery import shared_task, Celery

from tasks.models import UserSummary

from django.conf import settings


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'task_tracker.settings')

app = Celery('task_tracker', broker=settings.CELERY_BROKER_URL, backend=settings.CELERY_RESULT_BACKEND)
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


@shared_task
def update_total_time(total_time, summary_id):
    summary = UserSummary.objects.get(id=summary_id)
    summary.total_time = total_time
    summary.save()
