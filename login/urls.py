from django.urls import path
from .views import (
    MyTokenObtainPairView,
    MyTokenRefreshView,
    EmpresaCreateAPIView,
    RegistroEmpleadoAPIView,
    UsuarioCreateAPIView,
    BuscarEmpresaAPIView,
    SolicitarUnirseEmpresaPorNombreAPIView,
    AprobarSolicitudEmpleadoAPIView, 
    NotificacionListAPIView, 
    EliminarRelacionEmpleadoAPIView,
    ListarEmpleadosDeEmpresaAPIView
)
from rest_framework import permissions


urlpatterns = [
    path('api/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', MyTokenRefreshView.as_view(), name='token_refresh'),
    path('api/registro-empresa/', EmpresaCreateAPIView.as_view(), name='empresa_create'),    
    path('api/registro-empleado/', RegistroEmpleadoAPIView.as_view(), name='create_empleado'),
    path('api/registro_usuario/', UsuarioCreateAPIView.as_view(), name='create_user'),
    path('api/buscar-empresa/', BuscarEmpresaAPIView.as_view(), name='buscar_empresa'),
    path('api/solicitar-unirse/', SolicitarUnirseEmpresaPorNombreAPIView.as_view(), name='solicitar_unirse'),
    path('api/aprobar_solicitud/', AprobarSolicitudEmpleadoAPIView.as_view(), name='aprobar_solicitud'),
    path('api/notificaciones/', NotificacionListAPIView.as_view(), name='notificaciones'), 
    path('api/empresas/<str:empresa_nombre>/empleados/', ListarEmpleadosDeEmpresaAPIView.as_view(), name='empresa-empleados-listar'),
    path('api/empresas/<str:empresa_nombre>/empleados/<str:empleado_nombre>/eliminar/', EliminarRelacionEmpleadoAPIView.as_view(), name='empresa-empleado-eliminar'),
]
