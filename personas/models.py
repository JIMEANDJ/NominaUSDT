from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model 
from datetime import date
import requests


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
    correo = models.EmailField(unique=True, default='')
    usuarios = models.ManyToManyField(Usuario, through='EmpleadoEmpresa', related_name='empresas')
    creador = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='empresas_creadas', null=True, blank=True)
    saldo_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)  # Campo de saldo total

    def __str__(self):
        return self.nombre

    def agregar_saldo(self, monto):
        """Método para agregar saldo a la empresa"""
        self.saldo_total += monto
        self.save()

    def descontar_saldo(self, monto):
        """Método para descontar saldo de la empresa"""
        if self.saldo_total >= monto:
            self.saldo_total -= monto
            self.save()
        else:
            raise ValueError("Saldo insuficiente")

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
    tipo_cuenta = models.CharField(max_length=10, choices=[('corriente', 'Corriente'), ('ahorros', 'Ahorros')])
    numero_cuenta = models.CharField(max_length=50)
    documento_cuenta = models.CharField(max_length=50, choices=Empleado.TIPO_DOCUMENTO_CHOICES, default='')
    fecha_ultima_modificacion = models.DateTimeField(auto_now=True)  # Registra la fecha y hora de la última modificación

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
    
class Notificacion(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='notificaciones')
    mensaje = models.TextField()
    visto = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notificación para {self.usuario.username}: {self.mensaje[:20]}"

from django.contrib.auth import get_user_model

class RecargaUSDT(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, default='', related_name='recargas_usdt')
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)
    solana_tx_id = models.CharField(max_length=255, unique=True, default='')
    estado = models.CharField(
        max_length=20,
        choices=[('pendiente', 'Pendiente'), ('aprobado', 'Aprobado'), ('rechazado', 'Rechazado')],
        default='pendiente'
    )
    admin_validador = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True, related_name='recargas_validadas')
    fecha_validacion = models.DateTimeField(null=True, blank=True)  # Fecha de validación

    def __str__(self):
        return f"{self.empresa.nombre} - {self.cantidad} USDT ({self.estado})"

    def aprobar_recarga(self, admin):
        """Aprueba la recarga, asigna el validador y actualiza el saldo de la empresa."""
        if self.estado != 'pendiente':
            raise ValueError("La recarga ya ha sido procesada.")
        
        self.estado = 'aprobado'
        self.admin_validador = admin
        self.fecha_validacion = timezone.now()  # Registrar la fecha de validación
        self.empresa.agregar_saldo(self.cantidad)
        self.save()

    def rechazar_recarga(self, admin):
        """Rechaza la recarga y asigna el validador."""
        if self.estado != 'pendiente':
            raise ValueError("La recarga ya ha sido procesada.")
        
        self.estado = 'rechazado'
        self.admin_validador = admin
        self.fecha_validacion = timezone.now()  # Registrar la fecha de validación
        self.save()




class ComprobanteDePago(models.Model):
    orden_de_pago = models.OneToOneField('OrdenDePago', on_delete=models.CASCADE, related_name='comprobante')
    archivo = models.FileField(upload_to='comprobantes/')
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comprobante de {self.orden_de_pago}"


class OrdenDePago(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='ordenes_pago')
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='ordenes_pago')
    cantidad_usdt = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad_cop = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)

    def calcular_cop(self):
        """Convierte USDT a COP usando la tasa de Binance - 80 COP."""
        binance_rate = self.obtener_tasa_binance()
        return self.cantidad_usdt * (binance_rate - 80)

    @staticmethod
    def obtener_tasa_binance():
        """Obtiene la tasa de USDT a COP desde Binance."""
        url = 'https://api.binance.com/api/v3/ticker/price?symbol=USDTCOP'
        response = requests.get(url)
        data = response.json()
        return float(data['price'])

    def save(self, *args, **kwargs):
        self.cantidad_cop = self.calcular_cop()  # Calcula COP al guardar
        self.empresa.descontar_saldo(self.cantidad_usdt)  # Descontar saldo de la empresa
        super().save(*args, **kwargs)
