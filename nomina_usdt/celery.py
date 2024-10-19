# celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Establece la configuración de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nomina_usdt.settings')

app = Celery('nomina_usdt')

# Carga las configuraciones desde settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-detecta tareas en todos los archivos tasks.py en tus apps
app.autodiscover_tasks()
