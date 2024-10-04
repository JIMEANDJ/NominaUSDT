from rest_framework import serializers
from personas.models import Empresa, Empleado, Usuario, CuentaBancaria  # Ajusta la ruta de importación
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model

class UsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = get_user_model()
        fields = ['username', 'password', 'email', 'first_name', 'last_name']

    def create(self, validated_data):
        user = get_user_model().objects.create_user(**validated_data)
        return user

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Añadir datos adicionales
        token['nombre'] = user.first_name
        token['apellido'] = user.last_name
        token['correo'] = user.email
        return token

from rest_framework import serializers
from personas.models import Empresa

class EmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empresa
        fields = ['nombre', 'direccion', 'telefono']

class CuentaBancariaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CuentaBancaria
        fields = ['banco', 'tipo_cuenta', 'numero_cuenta']

from rest_framework import serializers
from django.contrib.auth import get_user_model
from personas.models import Empleado

from rest_framework import serializers
from personas.models import Empleado

class RegistroEmpleadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empleado
        fields = ['tipo_documento', 'documento_identidad', 'numero_telefono']

    def create(self, validated_data):
        # Obtener el usuario autenticado del contexto de la solicitud
        usuario = self.context['request'].user

        # Crear el empleado vinculado al usuario autenticado
        empleado = Empleado.objects.create(usuario=usuario, **validated_data)

        return empleado
