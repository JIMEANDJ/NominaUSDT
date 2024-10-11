from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model 
from datetime import date



class Usuario(AbstractUser):
    email = models.EmailField(unique=True)  # Hacer que el email sea único
    es_empresa = models.BooleanField(default=False)
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

    def __str__(self):
        return self.username

class Empresa(models.Model):
    nombre = models.CharField(max_length=255, default='', unique=True)
    direccion = models.CharField(max_length=255, default='')
    telefono = models.CharField(max_length=20, default='')
    usuarios = models.ManyToManyField(Usuario, through='EmpleadoEmpresa', related_name='empresas')
    creador = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='empresas_creadas', null=True, blank=True)

    def __str__(self):
        return self.nombre

class Empleado(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='empleado')
    TIPO_DOCUMENTO_CHOICES = [
        ('CC', 'Cédula de Ciudadanía'),
        ('CE', 'Cédula de Extranjería'),
        ('PASSPORT', 'Pasaporte'),
        ('PPT', 'Permiso por Protección Temporal'),
    ]
    tipo_documento = models.CharField(max_length=50, choices=TIPO_DOCUMENTO_CHOICES)
    documento_identidad = models.CharField(max_length=100, unique=True)
    numero_telefono = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.usuario.first_name} {self.usuario.last_name}"

class CuentaBancaria(models.Model):
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='cuentas_bancarias')
    banco = models.CharField(max_length=100)
    TIPO_CUENTA_CHOICES = [
        ('corriente', 'Corriente'),
        ('ahorros', 'Ahorros'),
    ]
    tipo_cuenta = models.CharField(max_length=10, choices=TIPO_CUENTA_CHOICES)
    numero_cuenta = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.banco} - {self.tipo_cuenta} - {self.numero_cuenta}"

class EmpleadoEmpresa(models.Model):
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='empleado_empresa')
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='empresa_empleado')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='usuario_empresa', default=1)
    cargo = models.CharField(max_length=100, default='Empleado')  # Nuevo campo cargo
    fecha_inicio = models.DateField(null=True, blank=True)  # Se llenará automáticamente cuando se apruebe
    estado = models.CharField(max_length=10, default='pendiente')  # Estado de la solicitud

    def __str__(self):
        return f"{self.empleado} - {self.empresa}"


class RecargaUSDT(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario} - {self.cantidad} USDT"

class OrdenDePago(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    cantidad_usdt = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad_cop = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Orden de pago para {self.empleado} de {self.cantidad_usdt} USDT"

class ComprobanteDePago(models.Model):
    orden_de_pago = models.OneToOneField(OrdenDePago, on_delete=models.CASCADE)
    archivo = models.FileField(upload_to='comprobantes/')
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comprobante de {self.orden_de_pago}"
