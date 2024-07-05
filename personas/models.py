from django.db import models
from django.contrib.auth.models import AbstractUser

# Modelo personalizado de usuario para permitir el login tanto de empleados como de empresas
class Usuario(AbstractUser):
    es_empresa = models.BooleanField(default=False)
    # Se añaden related_name únicos para evitar conflictos de acceso inverso
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name="usuario_groups",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="usuario_user_permissions",
        related_query_name="user",
    )

class Empresa(models.Model):
    nombre = models.CharField(max_length=255)
    usuarios = models.ManyToManyField(Usuario, through='EmpleadoEmpresa', related_name='empresas')

class Empleado(models.Model):
    nombre = models.CharField(max_length=255)
    apellido = models.CharField(max_length=255)
    tipo_documento = models.CharField(max_length=50)
    documento_identidad = models.CharField(max_length=100, unique=True)
    numero_telefono = models.CharField(max_length=20)
    correo = models.EmailField(unique=True)
    es_contribuyente = models.BooleanField(default=False)
    empresas = models.ManyToManyField(Empresa, through='EmpleadoEmpresa', related_name='empleados')

class EmpleadoEmpresa(models.Model):
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='empleado_empresa')
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='empresa_empleado')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)  # Añadir esta línea
    fecha_inicio = models.DateField() 
    fecha_fin = models.DateField(null=True, blank=True)

class RecargaUSDT(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)

class OrdenDePago(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    cantidad_usdt = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad_cop = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)

class ComprobanteDePago(models.Model):
    orden_de_pago = models.OneToOneField(OrdenDePago, on_delete=models.CASCADE)
    archivo = models.FileField(upload_to='comprobantes/')
    fecha = models.DateTimeField(auto_now_add=True)
