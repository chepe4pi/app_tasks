web: SERVER_INSTANCE=web gunicorn task_tracker.wsgi --workers 2 --threads 4
release: python manage.py migrate && python manage.py collectstatic --noinput
