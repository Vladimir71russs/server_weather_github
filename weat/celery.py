from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

# Указываем Django настройки для Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'weat.settings')
app = Celery('weat')

# Загружаем настройки из Django конфигурации, используя namespace 'CELERY'
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически регистрируем задачи из приложений
app.autodiscover_tasks()

# Добавьте это в конфигурацию вашего Celery
broker_connection_retry_on_startup = True
