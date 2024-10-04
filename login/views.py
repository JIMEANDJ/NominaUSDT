from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema
from personas.models import Empleado, Empresa
from .serializers import (
    UsuarioSerializer,
    MyTokenObtainPairSerializer,
    EmpresaSerializer,
    RegistroEmpleadoSerializer
)
from .permissions import AllowPartialAccess  # Asegúrate de que este permiso esté definido en tu proyecto


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
