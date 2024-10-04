from django.db import models
from django.contrib.auth.models import User


class TaskItem(models.Model):
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'

    PRIORITY_CHOICES = [
        (LOW, 'Low'),
        (MEDIUM, 'Medium'),
        (HIGH, 'High'),
    ]

    title = models.CharField(max_length=100)
    description = models.TextField()
    priority = models.CharField(max_length=6, choices=PRIORITY_CHOICES)
    due_date = models.DateField()

    def __str__(self):
        return self.title


class TaskRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(TaskItem, on_delete=models.CASCADE)
    date_completed = models.DateField()
    time_spent = models.PositiveIntegerField(help_text="Time spent in minutes")

    def __str__(self):
        return f"{self.user.username} - {self.task.title} ({self.date_completed})"


class UserSummary(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    total_time = models.PositiveIntegerField(help_text="Time spent in minutes", null=True)
