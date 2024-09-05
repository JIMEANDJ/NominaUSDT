# login/serializers.py

from rest_framework import serializers
from personas.models import Empresa, Empleado  # Ajusta la ruta de importación

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