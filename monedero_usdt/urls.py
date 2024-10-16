from django.urls import path
from .views import (
    SolicitarRecargaUSDTAPIView,
    AprobarRecargaUSDTAPIView,
    EliminarRelacionEmpleadoAPIView,
    ListarEmpleadosDeEmpresaAPIView
)

urlpatterns = [
    path('recargas/', SolicitarRecargaUSDTAPIView.as_view(), name='solicitar-recarga-usdt'),
    path('recargas/aprobar/', AprobarRecargaUSDTAPIView.as_view(), name='aprobar-recarga-usdt'),
    path('empresas/<str:nombre_empresa>/empleados/', ListarEmpleadosDeEmpresaAPIView.as_view(), name='listar-empleados-empresa'),
    path('empresas/<str:nombre_empresa>/empleados/<str:empleado_nombre>/eliminar/', EliminarRelacionEmpleadoAPIView.as_view(), name='eliminar-relacion'),
]
