web: gunicorn email_automation.wsgi:application 
celery: celery -A email_automation worker -l error 
beat: celery -A email_automation -l error -B --scheduler django_celery_beat.schedulers:DatabaseScheduler
