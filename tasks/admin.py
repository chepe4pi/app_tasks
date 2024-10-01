from django.contrib import admin
from .models import TaskItem, TaskRecord


@admin.register(TaskItem)
class TaskItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'priority', 'due_date')
    search_fields = ('title', 'description')
    list_filter = ('priority', 'due_date')


@admin.register(TaskRecord)
class TaskRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'task', 'date_completed', 'time_spent')
    search_fields = ('task__title', 'user__username')
    list_filter = ('date_completed', 'task__priority')
