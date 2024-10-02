from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth import get_user_model
from personas.models import Empleado, CuentaBancaria, Empresa
from .serializers import (
    UsuarioSerializer,
    MyTokenObtainPairSerializer,
    RegistroEmpleadoSerializer,
    CuentaBancariaSerializer,
    EmpresaSerializer
)

# Vista para la creación del Usuario
class UsuarioCreateAPIView(generics.CreateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UsuarioSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Usuario creado exitosamente"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Vista para obtener el Token JWT
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class MyTokenRefreshView(TokenRefreshView):
    pass

# Vista para registrar un empleado (debe estar autenticado con JWT)
class RegistroEmpleadoAPIView(APIView):
    permission_classes = [IsAuthenticated]  # Requiere que el usuario esté autenticado

    def post(self, request, *args, **kwargs):
        # El usuario ya debe estar autenticado y registrado (token JWT)
        serializer = RegistroEmpleadoSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Empleado registrado exitosamente"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Vista para agregar información de cuenta bancaria (opcional, al efectuar un pago)
class CuentaBancariaCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]  # El usuario debe estar autenticado

    def post(self, request, *args, **kwargs):
        # Se asume que el usuario ya es un empleado registrado
        empleado = request.user.empleado  # Se obtiene el empleado asociado al usuario autenticado
        serializer = CuentaBancariaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(empleado=empleado)
            return Response({"message": "Cuenta bancaria registrada exitosamente"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Vista para la creación de Empresa
class EmpresaCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]  # El usuario debe estar autenticado

    def post(self, request, *args, **kwargs):
        # El usuario debe estar autenticado para crear una empresa
        serializer = EmpresaSerializer(data=request.data)
        if serializer.is_valid():
            empresa = serializer.save()
            empresa.usuarios.add(request.user)  # Añadir al usuario autenticado como miembro de la empresa
            return Response({"message": "Empresa registrada exitosamente"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
