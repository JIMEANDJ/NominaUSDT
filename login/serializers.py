# login/serializers.py

from rest_framework import serializers
from personas.models import Empresa, Empleado  # Ajusta la ruta de importación
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from rest_framework import serializers
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
class RegistroEmpleadoSerializer(serializers.ModelSerializer):
    # Campos adicionales para la creación de un Usuario
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField()

    class Meta:
        model = Empleado
        fields = ['username', 'password', 'email', 'nombre', 'apellido', 'tipo_documento', 'documento_identidad', 'numero_telefono', 'es_contribuyente']

    def create(self, validated_data):
        # Extraer datos del usuario
        username = validated_data.pop('username')
        password = validated_data.pop('password')
        email = validated_data.pop('email')

        # Crear el usuario
        usuario = Usuario.objects.create_user(username=username, password=password, email=email)

        # Crear el empleado asociado
        empleado = Empleado.objects.create(usuario=usuario, **validated_data)
        
        return empleado