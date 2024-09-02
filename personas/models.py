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

    def __str__(self):
        return self.username

class Empresa(models.Model):
    nombre = models.CharField(max_length=255)
    usuarios = models.ManyToManyField(Usuario, through='EmpleadoEmpresa', related_name='empresas')

    def __str__(self):
        return self.nombre

class Empleado(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='empleado')
    nombre = models.CharField(max_length=255)
    apellido = models.CharField(max_length=255)
    tipo_documento = models.CharField(max_length=50)
    documento_identidad = models.CharField(max_length=100, unique=True)
    numero_telefono = models.CharField(max_length=20)
    correo = models.EmailField(unique=True)
    es_contribuyente = models.BooleanField(default=False)
    empresas = models.ManyToManyField(Empresa, through='EmpleadoEmpresa', related_name='empleados')

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

class EmpleadoEmpresa(models.Model):
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='empleado_empresa')
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='empresa_empleado')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='usuario_empresa', default=1)
    fecha_inicio = models.DateField() 
    fecha_fin = models.DateField(null=True, blank=True)

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
        return f"Orden de {self.empresa} a {self.empleado} - {self.cantidad_usdt} USDT"

class ComprobanteDePago(models.Model):
    orden_de_pago = models.OneToOneField(OrdenDePago, on_delete=models.CASCADE)
    archivo = models.FileField(upload_to='comprobantes/')
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comprobante de {self.orden_de_pago}"