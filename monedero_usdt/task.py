# tasks.py

from celery import shared_task
from .models import Notificacion, Usuario

@shared_task
def crear_notificacion_task(usuario_id, mensaje):
    try:
        usuario = Usuario.objects.get(id=usuario_id)
        Notificacion.objects.create(usuario=usuario, mensaje=mensaje)
    except Usuario.DoesNotExist:
        print(f"Usuario con ID {usuario_id} no encontrado.")
