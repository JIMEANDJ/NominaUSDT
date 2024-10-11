from rest_framework import serializers
from personas.models import Empresa, Empleado, Usuario, CuentaBancaria, EmpleadoEmpresa
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

class SolicitudUnirseEmpresaSerializer(serializers.ModelSerializer):
    cargo = serializers.CharField(required=True)

    class Meta:
        model = EmpleadoEmpresa
        fields = ['empleado', 'empresa', 'cargo', 'estado']
        read_only_fields = ['estado']  # Solo será "pendiente" al principio

    def validate(self, data):
        # Validar que no exista una solicitud pendiente o aprobada para el mismo empleado y empresa
        if EmpleadoEmpresa.objects.filter(empleado=data['empleado'], empresa=data['empresa'], estado__in=['pendiente', 'aprobado']).exists():
            raise serializers.ValidationError("Ya existe una solicitud pendiente o aprobada para esta empresa.")
        return data
