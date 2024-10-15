from rest_framework import serializers
from personas.models import Empresa, Empleado, Usuario, CuentaBancaria, EmpleadoEmpresa, Notificacion
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
        fields = ['id', 'empleado', 'empresa', 'cargo', 'estado']  # El campo 'id' será incluido automáticamente
        read_only_fields = ['id', 'estado']  # El campo 'id' es de solo lectura porque es auto-generado

    def validate(self, data):
        # Validar que no exista una solicitud pendiente o aprobada para el mismo empleado y empresa
        if EmpleadoEmpresa.objects.filter(empleado=data['empleado'], empresa=data['empresa'], estado__in=['pendiente', 'aprobado']).exists():
            raise serializers.ValidationError("Ya existe una solicitud pendiente o aprobada para esta empresa.")
        return data


class AprobarSolicitudEmpleadoSerializer(serializers.Serializer):
    solicitud_id = serializers.IntegerField()
    accion = serializers.ChoiceField(choices=[('aprobar', 'Aprobar'), ('rechazar', 'Rechazar')])

    class Meta:
        model = EmpleadoEmpresa
        fields = ['solicitud_id', 'accion']

    def update(self, instance, validated_data):
        # Obtener la acción (aprobar o rechazar)
        accion = validated_data.get('accion')

        if accion == 'aprobar':
            instance.estado = 'aprobado'
            instance.fecha_inicio = date.today()  # Asigna la fecha actual como fecha de inicio
        elif accion == 'rechazar':
            instance.estado = 'rechazado'

        instance.save()
        return instance

    def to_representation(self, instance):
        # Sobrescribir este método para incluir el ID de la solicitud en la respuesta
        representation = super().to_representation(instance)
        representation['solicitud_id'] = instance.id  # Añadir el ID de la solicitud
        return representation




class NotificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notificacion
        fields = ['id', 'mensaje', 'visto', 'fecha_creacion']
        
        
class EliminarRelacionEmpleadoSerializer(serializers.Serializer):
    mensaje = serializers.CharField()
    
class EmpleadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empleado
        fields = ['id', 'nombre', 'apellido', 'email']  # Campos que quieras incluir

