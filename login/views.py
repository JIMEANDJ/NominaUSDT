from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema
from personas.models import Empleado, Empresa, Notificacion
from .serializers import (
    UsuarioSerializer,
    MyTokenObtainPairSerializer,
    EmpresaSerializer,
    RegistroEmpleadoSerializer,
    AprobarSolicitudEmpleadoSerializer, 
    NotificacionSerializer, 
    EliminarRelacionEmpleadoSerializer,
    EmpleadoSerializer
)
from .permissions import AllowPartialAccess  # Asegúrate de que este permiso esté definido en tu proyecto

from django.core.mail import send_mail
from django.conf import settings

from personas.models import EmpleadoEmpresa
from datetime import date



# Vista para creación de usuarios (con correo, nombre completo y contraseña)
class UsuarioCreateAPIView(generics.CreateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UsuarioSerializer

    @swagger_auto_schema(request_body=UsuarioSerializer)
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


# Vista para obtener el token JWT (incluyendo datos extra como nombre, apellido y correo)
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

    @swagger_auto_schema(request_body=MyTokenObtainPairSerializer)
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


# Vista para refrescar el token JWT
class MyTokenRefreshView(TokenRefreshView):
    pass


# Vista para creación de empresas
class EmpresaCreateAPIView(APIView):
    @swagger_auto_schema(request_body=EmpresaSerializer)
    def post(self, request, *args, **kwargs):
        serializer = EmpresaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Vista para registro de empleados (requiere JWT Token válido)

from rest_framework.permissions import IsAuthenticated

class RegistroEmpleadoAPIView(APIView):
    permission_classes = [IsAuthenticated]  # Asegurarse de que el usuario esté autenticado

    @swagger_auto_schema(request_body=RegistroEmpleadoSerializer)
    def post(self, request, *args, **kwargs):
        serializer = RegistroEmpleadoSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BuscarEmpresaAPIView(generics.ListAPIView):
    serializer_class = EmpresaSerializer

    def get_queryset(self):
        nombre_empresa = self.request.query_params.get('nombre', None)
        if nombre_empresa:
            return Empresa.objects.filter(nombre__icontains=nombre_empresa)
        return Empresa.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({"mensaje": "No se encontraron empresas"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)



class SolicitarUnirseEmpresaPorNombreAPIView(APIView):
    def post(self, request, *args, **kwargs):
        empleado_nombre = request.data.get('empleado_nombre')
        empresa_nombre = request.data.get('empresa_nombre')
        cargo = request.data.get('cargo')  # Se añade el campo cargo
        
        try:
            empleado = Empleado.objects.get(usuario__username=empleado_nombre)
            empresa = Empresa.objects.get(nombre=empresa_nombre)
        except Empleado.DoesNotExist:
            return Response({"error": "Empleado no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        except Empresa.DoesNotExist:
            return Response({"error": "Empresa no encontrada"}, status=status.HTTP_404_NOT_FOUND)

        # Crear la solicitud de relación empleado-empresa con estado "pendiente"
        relacion = EmpleadoEmpresa.objects.create(empleado=empleado, empresa=empresa, estado='pendiente', cargo=cargo)
        
        # Devolver la respuesta con el ID de la solicitud creada
        return Response({
            "mensaje": "Solicitud enviada, pendiente de aprobación",
            "solicitud_id": relacion.id  # Devolver el ID de la solicitud generada
        }, status=status.HTTP_201_CREATED)
class AprobarSolicitudEmpleadoAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = AprobarSolicitudEmpleadoSerializer(data=request.data)
        if serializer.is_valid():
            solicitud_id = serializer.validated_data['solicitud_id']
            accion = serializer.validated_data['accion']
            
            try:
                solicitud = EmpleadoEmpresa.objects.get(id=solicitud_id)
            except EmpleadoEmpresa.DoesNotExist:
                return Response({"error": "Solicitud no encontrada"}, status=status.HTTP_404_NOT_FOUND)
            
            if accion == 'aprobar':
                solicitud.estado = 'aprobado'
                solicitud.fecha_inicio = date.today()  # Asigna la fecha actual como fecha de inicio
                solicitud.save()
                
                # Crear notificación para el empleado
                mensaje = f'Tu solicitud para unirte a la empresa {solicitud.empresa.nombre} ha sido aprobada.'
                Notificacion.objects.create(usuario=solicitud.empleado.usuario, mensaje=mensaje)

                return Response({"mensaje": "Solicitud aprobada"}, status=status.HTTP_200_OK)
            
            elif accion == 'rechazar':
                solicitud.estado = 'rechazado'
                solicitud.save()

                # Crear notificación para el empleado
                mensaje = f'Tu solicitud para unirte a la empresa {solicitud.empresa.nombre} ha sido rechazada.'
                Notificacion.objects.create(usuario=solicitud.empleado.usuario, mensaje=mensaje)

                return Response({"mensaje": "Solicitud rechazada"}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NotificacionListAPIView(APIView):
    def get(self, request, *args, **kwargs):
        notificaciones = Notificacion.objects.filter(usuario=request.user).order_by('-fecha_creacion')
        serializer = NotificacionSerializer(notificaciones, many=True)
        return Response(serializer.data)



class EliminarRelacionEmpleadoAPIView(APIView):
    def delete(self, request, empleado_id, empresa_id):
        try:
            relacion = EmpleadoEmpresa.objects.get(empleado__id=empleado_id, empresa__id=empresa_id)
            relacion.delete()
            return Response({"mensaje": "Relación eliminada correctamente"}, status=status.HTTP_200_OK)
        except EmpleadoEmpresa.DoesNotExist:
            return Response({"error": "Relación no encontrada"}, status=status.HTTP_404_NOT_FOUND)




class ListarEmpleadosDeEmpresaAPIView(APIView):
    def get(self, request, empresa_id):
        try:
            empresa = Empresa.objects.get(id=empresa_id)
        except Empresa.DoesNotExist:
            return Response({"error": "Empresa no encontrada"}, status=status.HTTP_404_NOT_FOUND)
        
        # Obtener la lista de empleados relacionados con la empresa
        empleados = Empleado.objects.filter(empleadoempresa__empresa=empresa)
        
        # Serializar los datos de los empleados
        serializer = EmpleadoSerializer(empleados, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)





#from django.core.mail import send_mail
#from django.conf import settings


'''class SolicitarUnirseEmpresaPorNombreAPIView(APIView):
    def post(self, request, *args, **kwargs):
        empleado_nombre = request.data.get('empleado_nombre')
        empresa_nombre = request.data.get('empresa_nombre')
        cargo = request.data.get('cargo')  # Se añade el campo cargo
        
        try:
            empleado = Empleado.objects.get(usuario__username=empleado_nombre)
            empresa = Empresa.objects.get(nombre=empresa_nombre)
        except Empleado.DoesNotExist:
            return Response({"error": "Empleado no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        except Empresa.DoesNotExist:
            return Response({"error": "Empresa no encontrada"}, status=status.HTTP_404_NOT_FOUND)

        # Crear la solicitud de relación empleado-empresa con estado "pendiente"
        relacion = EmpleadoEmpresa.objects.create(empleado=empleado, empresa=empresa, estado='pendiente', cargo=cargo)
        
        # Generar un enlace de aprobación/desaprobación
        # Supongamos que tienes una URL en el front para manejar esto
        link_aprobacion = f"https://tuapp.com/empresa/solicitud/{relacion.id}/aprobar"
        link_rechazo = f"https://tuapp.com/empresa/solicitud/{relacion.id}/rechazar"
        
        # Enviar correo desde el correo de la app a la empresa
        send_mail(
            subject='Nueva solicitud de empleado',
            message=f'El empleado {empleado_nombre} ha solicitado unirse a la empresa {empresa_nombre} para el cargo de {cargo}.\n\n'
                    f'Puedes aprobar o rechazar la solicitud en los siguientes enlaces:\n'
                    f'Aprobar: {link_aprobacion}\n'
                    f'Rechazar: {link_rechazo}',
            from_email=settings.DEFAULT_FROM_EMAIL,  # Configurado en tu settings.py
            recipient_list=[empresa.correo],  # Asumiendo que Empresa tiene un campo 'correo' que es el email del admin
        )

        return Response({"mensaje": "Solicitud enviada, pendiente de aprobación"}, status=status.HTTP_201_CREATED)
class AprobarSolicitudEmpleadoAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = AprobarSolicitudEmpleadoSerializer(data=request.data)
        if serializer.is_valid():
            solicitud_id = serializer.validated_data['solicitud_id']
            accion = serializer.validated_data['accion']
            
            try:
                solicitud = EmpleadoEmpresa.objects.get(id=solicitud_id)
            except EmpleadoEmpresa.DoesNotExist:
                return Response({"error": "Solicitud no encontrada"}, status=status.HTTP_404_NOT_FOUND)
            
            if accion == 'aprobar':
                solicitud.estado = 'aprobado'
                solicitud.fecha_inicio = date.today()  # Asigna la fecha actual como fecha de inicio
                solicitud.save()
                
                # Enviar correo al empleado notificando que la solicitud fue aprobada
                send_mail(
                    subject='Solicitud aprobada',
                    message=f'Tu solicitud para unirte a la empresa {solicitud.empresa.nombre} ha sido aprobada.',
                    from_email=settings.DEFAULT_FROM_EMAIL,  # Enviar desde el correo de la app
                    recipient_list=[solicitud.empleado.usuario.email],  # Correo del empleado
                )

                return Response({"mensaje": "Solicitud aprobada"}, status=status.HTTP_200_OK)
            
            elif accion == 'rechazar':
                solicitud.estado = 'rechazado'
                solicitud.save()

                # Enviar correo al empleado notificando que la solicitud fue rechazada
                send_mail(
                    subject='Solicitud rechazada',
                    message=f'Tu solicitud para unirte a la empresa {solicitud.empresa.nombre} ha sido rechazada.',
                    from_email=settings.DEFAULT_FROM_EMAIL,  # Enviar desde el correo de la app
                    recipient_list=[solicitud.empleado.usuario.email],  # Correo del empleado
                )

                return Response({"mensaje": "Solicitud rechazada"}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)''' 
