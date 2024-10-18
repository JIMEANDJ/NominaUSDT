from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import RecargaUSDTSerializer, AprobarRecargaSerializer, OrdenDePagoSerializer, ComprobanteDePagoSerializer
from personas.models import RecargaUSDT, Notificacion, CuentaBancaria, OrdenDePago, Empresa, Usuario, ComprobanteDePago

import requests
import time
from solana.rpc.api import Client as SolanaClient
from tronpy import Tron as TronClient

# Configuración global
MAX_RETRIES = 6  # Número de reintentos (cada reintento será cada 5 minutos)
WAIT_TIME = 5 * 60  # 5 minutos en segundos

# Clientes RPC
solana_client = SolanaClient("https://api.mainnet-beta.solana.com")
tron_client = TronClient()

# Función para validar transacción en Solana
def validar_transaccion_solana(solana_tx_id, monto_esperado, wallet_address):
    try:
        response = solana_client.get_confirmed_transaction(solana_tx_id)
        if response['result'] is None:
            return {"status": "pendiente", "message": "Transacción aún no confirmada en Solana."}

        transaction_info = response['result']['transaction']
        post_balances = transaction_info['meta']['postBalances']
        pre_balances = transaction_info['meta']['preBalances']
        accounts = transaction_info['transaction']['message']['accountKeys']

        for account in accounts:
            if account == wallet_address:
                for pre_balance, post_balance in zip(pre_balances, post_balances):
                    if post_balance - pre_balance == monto_esperado:
                        return {"status": "success", "amount": monto_esperado}
        return {"status": "error", "message": "Monto no coincide o wallet no involucrada."}
    except Exception as e:
        return {"status": "error", "message": f"Error al consultar la transacción: {str(e)}"}

# Función para validar transacción en Tron
def validar_transaccion_tron(tron_tx_id, monto_esperado, wallet_address):
    try:
        txn_info = tron_client.get_transaction_info(tron_tx_id)
        if txn_info is None or txn_info['receipt']['result'] != 'SUCCESS':
            return {"status": "pendiente", "message": "Transacción aún no confirmada en Tron."}

        transfer_event = [event for event in txn_info['log'] if event['address'] == wallet_address]
        if transfer_event:
            if int(transfer_event[0]['data'], 16) == monto_esperado * 10**6:  # TRC20 tokens tienen 6 decimales
                return {"status": "success", "amount": monto_esperado}
        return {"status": "error", "message": "Monto no coincide o wallet no involucrada."}
    except Exception as e:
        return {"status": "error", "message": f"Error al consultar la transacción: {str(e)}"}

# Función para elegir y validar la transacción según el tipo de blockchain
def validar_transaccion(solana_tx_id, tron_tx_id, monto_esperado):
    blockchain_type = settings.BLOCKCHAIN_TYPE
    if blockchain_type == 'solana':
        return validar_transaccion_solana(solana_tx_id, monto_esperado, settings.SOLANA_WALLET_ADDRESS)
    elif blockchain_type == 'tron':
        return validar_transaccion_tron(tron_tx_id, monto_esperado, settings.TRON_WALLET_ADDRESS)
    else:
        return {"status": "error", "message": "Blockchain no soportada."}

# Función para enviar notificaciones de fallo
def enviar_notificacion_fallo_validacion(recarga, admin):
    mensaje = (f"La empresa {recarga.empresa.nombre} ha enviado una transferencia de {recarga.cantidad} USDT, "
               f"pero no se ha podido validar en 30 minutos. Por favor, contactar a la empresa.\n"
               f"ID de Recarga: {recarga.id}\n"
               f"ID de Transacción: {recarga.solana_tx_id if settings.BLOCKCHAIN_TYPE == 'solana' else recarga.tron_tx_id}\n"
               f"Administrador: {admin.username}")
    send_mail(
        subject="Alerta de transacción no validada",
        message=mensaje,
        from_email="soporte@tuapp.com",
        recipient_list=["soporte@tuapp.com"]
    )

# Vista para solicitar recarga
class SolicitarRecargaUSDTAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = RecargaUSDTSerializer(data=request.data)
        if serializer.is_valid():
            recarga = serializer.save()
            return Response({
                "mensaje": "Solicitud de recarga enviada, pendiente de aprobación.",
                "solicitud_id": recarga.id
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Vista para validar recarga
class ValidarRecargaUSDTView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, recarga_id, *args, **kwargs):
        try:
            recarga = RecargaUSDT.objects.get(id=recarga_id)
            if recarga.estado != 'pendiente':
                return Response({"message": "La recarga ya ha sido procesada."}, status=status.HTTP_400_BAD_REQUEST)

            for retry in range(MAX_RETRIES):
                validacion = validar_transaccion(recarga.solana_tx_id, recarga.tron_tx_id, recarga.cantidad)
                if validacion["status"] == "success":
                    if recarga.cantidad != validacion['amount']:
                        recarga.cantidad = validacion['amount']
                    recarga.aprobar_recarga(admin=request.user)
                    return Response({
                        "message": f"Recarga aprobada. Monto validado: {validacion['amount']} USDT.",
                        "admin_validador": request.user.username,
                        "fecha_validacion": recarga.fecha_validacion
                    }, status=status.HTTP_200_OK)
                elif validacion["status"] == "error":
                    return Response({"message": validacion["message"]}, status=status.HTTP_400_BAD_REQUEST)
                time.sleep(WAIT_TIME)

            enviar_notificacion_fallo_validacion(recarga, request.user)
            return Response({
                "message": "Transacción no validada en 30 minutos. Contactaremos al soporte."
            }, status=status.HTTP_408_REQUEST_TIMEOUT)
        except RecargaUSDT.DoesNotExist:
            return Response({"message": "Recarga no encontrada."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": f"Error interno: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Vista para obtener la dirección de la wallet USDT
class ObtenerWalletUSDTView(APIView):
    def get(self, request, *args, **kwargs):
        wallet_address = settings.SOLANA_WALLET_ADDRESS
        network_type = settings.NETWORK_TYPE
        return Response({
            "wallet_address": wallet_address,
            "network_type": network_type
        }, status=status.HTTP_200_OK)


class ModificarCuentaBancariaAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        empleado = request.user.empleado  # Se asume que el usuario es un empleado autenticado
        serializer = CuentaBancariaSerializer(data=request.data)

        if serializer.is_valid():
            cuenta_bancaria, created = CuentaBancaria.objects.update_or_create(
                empleado=empleado,
                defaults=serializer.validated_data
            )
            mensaje = "Cuenta bancaria creada." if created else "Cuenta bancaria actualizada."
            return Response({"mensaje": mensaje}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListarCuentasBancariasEmpleadosAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, empresa_id, *args, **kwargs):
        try:
            empresa = Empresa.objects.get(id=empresa_id, usuarios=request.user)
            empleados = empresa.empresa_empleado.filter(estado='aprobado').select_related('empleado__usuario')
            data = [
                {
                    "nombre": f"{empleado.empleado.usuario.first_name} {empleado.empleado.usuario.last_name}",
                    "cuenta_bancaria": {
                        "banco": empleado.empleado.cuentas_bancarias.first().banco,
                        "tipo_cuenta": empleado.empleado.cuentas_bancarias.first().tipo_cuenta,
                        "numero_cuenta": empleado.empleado.cuentas_bancarias.first().numero_cuenta
                    }
                } for empleado in empleados
            ]
            return Response(data, status=status.HTTP_200_OK)

        except Empresa.DoesNotExist:
            return Response({"mensaje": "Empresa no encontrada o no tiene permisos."}, status=status.HTTP_404_NOT_FOUND)


class ObtenerTasaUSDTAPIView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            url = 'https://api.binance.com/api/v3/ticker/price?symbol=USDTCOP'
            response = requests.get(url)
            data = response.json()
            tasa_usdt = float(data['price'])
            tasa_ajustada = tasa_usdt - 80  # Tasa ajustada con -80 COP

            return Response({
                "tasa_binance": tasa_usdt,
                "tasa_ajustada": tasa_ajustada,
                "mensaje": f"1 USDT = {tasa_ajustada} COP"
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"mensaje": f"Error al obtener la tasa: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class CrearOrdenDePagoView(generics.CreateAPIView):
    serializer_class = OrdenDePagoSerializer

    def perform_create(self, serializer):
        # Guardar la orden de pago
        orden_de_pago = serializer.save()

        # Descontar el saldo de la empresa
        empresa = orden_de_pago.empresa
        empresa.descontar_saldo(orden_de_pago.cantidad_usdt)

        # Notificación para la empresa
        notificacion_empresa = Notificacion.objects.create(
            usuario=empresa.creador,
            mensaje=f"Se ha enviado un pago a {orden_de_pago.empleado.usuario.first_name} {orden_de_pago.empleado.usuario.last_name}. ID de transferencia: {orden_de_pago.id}."
        )

        # Notificación para el empleado
        notificacion_empleado = Notificacion.objects.create(
            usuario=orden_de_pago.empleado.usuario,
            mensaje=f"La empresa {empresa.nombre} te ha enviado {orden_de_pago.cantidad_cop} COP. ID de transferencia: {orden_de_pago.id}."
        )

        # Notificación para el admin (para realizar la transferencia)
        admin = Usuario.objects.filter(is_superuser=True).first()
        notificacion_admin = Notificacion.objects.create(
            usuario=admin,
            mensaje=f"Realiza la transferencia para la empresa {empresa.nombre}. ID de transferencia: {orden_de_pago.id}."
        )
        
        
    
class SubirComprobanteDePagoView(generics.CreateAPIView):
    serializer_class = ComprobanteDePagoSerializer
    parser_classes = [MultiPartParser]

    def perform_create(self, serializer):
        comprobante = serializer.save()

        # Notificación para la empresa
        empresa = comprobante.orden_de_pago.empresa
        Notificacion.objects.create(
            usuario=empresa.creador,
            mensaje=f"Transferencia ID {comprobante.orden_de_pago.id} ha sido realizada con éxito."
        )

        # Notificación para el empleado
        empleado = comprobante.orden_de_pago.empleado
        Notificacion.objects.create(
            usuario=empleado.usuario,
            mensaje=f"La transferencia ID {comprobante.orden_de_pago.id} por {comprobante.orden_de_pago.cantidad_cop} COP ha sido realizada con éxito."
        )
        

            
            

class ListaOrdenesPagoEmpresaView(generics.ListAPIView):
    serializer_class = OrdenDePagoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        empresa = self.request.user.empresa_set.first()  # Suponiendo que una empresa tiene un único creador
        return OrdenDePago.objects.filter(empresa=empresa)
    
class ListaOrdenesPagoEmpleadoView(generics.ListAPIView):
    serializer_class = OrdenDePagoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        empleado = self.request.user.empleado
        return OrdenDePago.objects.filter(empleado=empleado)
    
class ComprobantePorOrdenView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, orden_id, *args, **kwargs):
        try:
            # Buscar la orden de pago por ID
            orden = OrdenDePago.objects.get(id=orden_id)
            
            # Verificar si la orden tiene un comprobante asociado
            if not hasattr(orden, 'comprobante'):
                raise NotFound("No hay comprobante asociado a esta orden de pago.")
            
            # Si existe, devolver el URL del comprobante
            comprobante_url = request.build_absolute_uri(orden.comprobante.archivo.url)
            return Response({"comprobante_url": comprobante_url})
        except OrdenDePago.DoesNotExist:
            raise NotFound("No existe una orden de pago con esta ID.")
        