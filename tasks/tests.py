from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from .models import TaskItem, TaskRecord
from django.utils import timezone


class BaseTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user', password='password')
        self.obtain_token()

    def obtain_token(self):
        url = reverse('token_obtain_pair')
        response = self.client.post(url, {'username': 'user', 'password': 'password'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)


class TaskItemTests(BaseTestCase):
    def test_create_task(self):
        url = reverse('taskitem-list')
        data = {
            'title': 'Test Task',
            'description': 'Test Description',
            'priority': 'medium',
            'due_date': '2023-12-31'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Test Task WITH ERROR')

    def test_list_tasks(self):
        TaskItem.objects.create(title='Task 1', description='Description 1', priority='medium', due_date='2023-12-31')
        TaskItem.objects.create(title='Task 2', description='Description 2', priority='high', due_date='2023-12-31')

        url = reverse('taskitem-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve_task(self):
        task = TaskItem.objects.create(title='Task 1', description='Description 1', priority='medium',
                                       due_date='2023-12-31')
        url = reverse('taskitem-detail', args=[task.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Task 1')

    def test_update_task(self):
        task = TaskItem.objects.create(title='Task 1', description='Description 1', priority='medium',
                                       due_date='2023-12-31')
        url = reverse('taskitem-detail', args=[task.id])
        data = {
            'title': 'Updated Task',
            'description': 'Updated Description',
            'priority': 'high',
            'due_date': '2023-12-25'
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Task')

    def test_delete_task(self):
        task = TaskItem.objects.create(title='Task 1', description='Description 1', priority='medium',
                                       due_date='2023-12-31')
        url = reverse('taskitem-detail', args=[task.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(TaskItem.objects.filter(id=task.id).exists())


class TaskRecordTests(BaseTestCase):
    def test_create_task_record(self):
        # Ensure task item is created first
        task = TaskItem.objects.create(title='Task 1', description='Description 1', priority='medium', due_date='2023-12-31')

        # Re-fetch the task to ensure it exists
        task = TaskItem.objects.get(title='Task 1')

        url = reverse('taskrecord-list')
        data = {
            'user': self.user.id,
            'task': task.id,  # Use the correct task ID
            'date_completed': timezone.now().date().isoformat(),  # Ensure date format is correct
            'time_spent': 60
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(response.data['time_spent'], 60)

    def test_list_task_records(self):
        task = TaskItem.objects.create(title='Task 1', description='Description 1', priority='medium',
                                       due_date='2023-12-31')
        TaskRecord.objects.create(user=self.user, task=task, date_completed=timezone.now().date(), time_spent=60)
        TaskRecord.objects.create(user=self.user, task=task, date_completed=timezone.now().date(), time_spent=120)

        url = reverse('taskrecord-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve_task_record(self):
        task = TaskItem.objects.create(title='Task 1', description='Description 1', priority='medium',
                                       due_date='2023-12-31')
        record = TaskRecord.objects.create(user=self.user, task=task, date_completed=timezone.now().date(),
                                           time_spent=60)

        url = reverse('taskrecord-detail', args=[record.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['time_spent'], 60)

    def test_update_task_record(self):
        task = TaskItem.objects.create(title='Task 1', description='Description 1', priority='medium',
                                       due_date='2023-12-31')
        record = TaskRecord.objects.create(user=self.user, task=task, date_completed=timezone.now().date(),
                                           time_spent=60)

        url = reverse('taskrecord-detail', args=[record.id])
        data = {
            'user': self.user.id,
            'task': task.id,
            'date_completed': timezone.now().date(),
            'time_spent': 90
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['time_spent'], 90)

    def test_delete_task_record(self):
        task = TaskItem.objects.create(title='Task 1', description='Description 1', priority='medium',
                                       due_date='2023-12-31')
        record = TaskRecord.objects.create(user=self.user, task=task, date_completed=timezone.now().date(),
                                           time_spent=60)

        url = reverse('taskrecord-detail', args=[record.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(TaskRecord.objects.filter(id=record.id).exists())


class SummaryTests(BaseTestCase):
    def test_daily_summary(self):
        date_completed = timezone.now().date()

        # Create TaskItems
        task1 = TaskItem.objects.create(title='Task 1', description='Description 1', priority='medium',
                                        due_date='2023-12-31')
        task2 = TaskItem.objects.create(title='Task 2', description='Description 2', priority='high',
                                        due_date='2023-12-31')
        task3 = TaskItem.objects.create(title='Task 3', description='Description 3', priority='low',
                                        due_date='2023-12-31')
        task4 = TaskItem.objects.create(title='Task 4', description='Description 4', priority='medium',
                                        due_date='2023-12-31')

        # Create TaskRecords
        TaskRecord.objects.create(user=self.user, task=task1, date_completed=date_completed, time_spent=60)
        TaskRecord.objects.create(user=self.user, task=task2, date_completed=date_completed, time_spent=120)
        TaskRecord.objects.create(user=self.user, task=task3, date_completed=date_completed, time_spent=30)
        TaskRecord.objects.create(user=self.user, task=task4, date_completed=date_completed, time_spent=45)

        url = reverse('summary-daily')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check values
        self.assertEqual(response.data['total_tasks'], 4)
        self.assertEqual(response.data['total_time_spent'], 255)
        self.assertEqual(response.data['priorities']['medium'], 2)
        self.assertEqual(response.data['priorities']['low'], 1)
        self.assertEqual(response.data['priorities']['high'], 1)