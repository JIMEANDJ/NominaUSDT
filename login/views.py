from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from personas.models import Empresa, Empleado
from .serializers import EmpresaSerializer, RegistroEmpleadoSerializer
from .permissions import AllowPartialAccess
from drf_yasg.utils import swagger_auto_schema


from rest_framework import generics
from django.contrib.auth import get_user_model
from .serializers import UsuarioSerializer

class UsuarioCreateAPIView(generics.CreateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UsuarioSerializer

    @swagger_auto_schema(request_body=UsuarioSerializer)
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Añadir datos adicionales
        token['nombre'] = user.first_name
        token['apellido'] = user.last_name
        token['correo'] = user.email
        return token

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

    @swagger_auto_schema(request_body=MyTokenObtainPairSerializer)
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class MyTokenRefreshView(TokenRefreshView):
    pass

class EmpresaCreateAPIView(APIView):
    permission_classes = [AllowPartialAccess]  # Usamos el permiso personalizado

    @swagger_auto_schema(request_body=EmpresaSerializer)
    def post(self, request, *args, **kwargs):
        serializer = EmpresaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RegistroEmpleadoAPIView(APIView):
    permission_classes = [AllowPartialAccess]  # Usamos el permiso personalizado

    @swagger_auto_schema(request_body=RegistroEmpleadoSerializer)
    def post(self, request):
        serializer = RegistroEmpleadoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
