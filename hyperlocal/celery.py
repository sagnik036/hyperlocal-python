import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hyperlocal.settings')

common_app = Celery('hyperlocal_common')
common_app.config_from_object('django.conf:settings', force=True, namespace='COMMON_CELERY')
common_app.autodiscover_tasks(['api'])



