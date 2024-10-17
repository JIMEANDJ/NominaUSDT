from django.urls import path
from .views import (
    SolicitarRecargaUSDTAPIView,
    AprobarRecargaUSDTAPIView,
    EliminarRelacionEmpleadoAPIView,
    ListarEmpleadosDeEmpresaAPIView
)

urlpatterns = [
    path('recargas/', SolicitarRecargaUSDTAPIView.as_view(), name='solicitar-recarga-usdt'),
    path('recargas/aprobar/', AValidarRecargaUSDTView.as_view(), name='aprobar-recarga-usdt'),


]
