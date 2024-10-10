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


class SolicitarUnirseEmpresaAPIView(APIView):
    def post(self, request, *args, **kwargs):
        empleado_id = request.data.get('empleado_id')
        empresa_id = request.data.get('empresa_id')
        
        try:
            empleado = Empleado.objects.get(id=empleado_id)
            empresa = Empresa.objects.get(id=empresa_id)
        except Empleado.DoesNotExist:
            return Response({"error": "Empleado no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        except Empresa.DoesNotExist:
            return Response({"error": "Empresa no encontrada"}, status=status.HTTP_404_NOT_FOUND)

        # Crear la solicitud de relación empleado-empresa con estado "pendiente"
        relacion = EmpleadoEmpresa.objects.create(empleado=empleado, empresa=empresa, estado='pendiente')
        return Response({"mensaje": "Solicitud enviada, pendiente de aprobación"}, status=status.HTTP_201_CREATED)


class AprobarSolicitudEmpleadoAPIView(APIView):
    def post(self, request, *args, **kwargs):
        solicitud_id = request.data.get('solicitud_id')
        accion = request.data.get('accion')  # "aprobar" o "rechazar"
        
        try:
            solicitud = EmpleadoEmpresa.objects.get(id=solicitud_id)
        except EmpleadoEmpresa.DoesNotExist:
            return Response({"error": "Solicitud no encontrada"}, status=status.HTTP_404_NOT_FOUND)
        
        if accion == 'aprobar':
            solicitud.estado = 'aprobado'
            solicitud.fecha_inicio = date.today()
            solicitud.save()
            return Response({"mensaje": "Solicitud aprobada"}, status=status.HTTP_200_OK)
        elif accion == 'rechazar':
            solicitud.estado = 'rechazado'
            solicitud.save()
            return Response({"mensaje": "Solicitud rechazada"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Acción no válida"}, status=status.HTTP_400_BAD_REQUEST)
