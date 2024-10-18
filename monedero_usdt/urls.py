from django.urls import path
from .views import (
    SolicitarRecargaUSDTAPIView,
    AprobarRecargaUSDTAPIView,
    EliminarRelacionEmpleadoAPIView,
    ListarEmpleadosDeEmpresaAPIView,
    ListaOrdenesPagoEmpresaView, 
    ListaOrdenesPagoEmpleadoView,
    CrearOrdenDePagoView,
    SubirComprobanteDePagoView,
    ComprobantePorOrdenView
    
)

urlpatterns = [
    path('recargas/', SolicitarRecargaUSDTAPIView.as_view(), name='solicitar-recarga-usdt'),
    path('recargas/aprobar/', AValidarRecargaUSDTView.as_view(), name='aprobar-recarga-usdt'),
    path('wallet/', ObtenerWalletUSDTView.as_view(), name='obtener-wallet-usdt'),  # Nueva ruta para obtener wallet
    path('ordenes-pago/', CrearOrdenDePagoView.as_view(), name='crear-orden-de-pago'),
    path('comprobantes-pago/', SubirComprobanteDePagoView.as_view(), name='subir-comprobante-pago'),
    path('ordenes-pago/<int:orden_id>/comprobante/', ComprobantePorOrdenView.as_view(), name='comprobante-por-orden'),
]

    

