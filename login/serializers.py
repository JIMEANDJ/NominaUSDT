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

class EmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empresa
        fields = '__all__'

class CuentaBancariaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CuentaBancaria
        fields = ['banco', 'tipo_cuenta', 'numero_cuenta']

class RegistroEmpleadoSerializer(serializers.ModelSerializer):
    # Campos adicionales para la creación de un Usuario
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField()
    nombre_y_apellido = serializers.CharField(source='usuario.first_name', write_only=True)
    apellido = serializers.CharField(source='usuario.last_name', write_only=True)

    class Meta:
        model = Empleado
        fields = ['password', 'email', 'nombre_y_apellido', 'apellido', 'tipo_documento', 'documento_identidad', 'numero_telefono'] 

    def create(self, validated_data):
        # Extraer datos del usuario
        password = validated_data.pop('password')
        email = validated_data.pop('email')
        nombre_y_apellido = validated_data.pop('usuario')['first_name']
        apellido = validated_data.pop('usuario')['last_name']

        # Crear el usuario
        usuario = Usuario.objects.create_user(
            username=nombre_y_apellido,  # Asigna un nombre de usuario basado en el nombre
            password=password,
            email=email,
            first_name=nombre_y_apellido,
            last_name=apellido
        )

        # Crear el empleado asociado
        empleado = Empleado.objects.create(usuario=usuario, **validated_data)

        return empleado
