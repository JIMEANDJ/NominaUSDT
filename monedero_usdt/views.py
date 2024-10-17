from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RecargaUSDTSerializer, AprobarRecargaSerializer
from personas.models import RecargaUSDT, Notificacion, CuentaBancaria
import requests
from django.utils import timezone
from rest_framework.permissions import IsAdminUser 
from django.conf import settings
from rest_framework.permissions import IsAuthenticated



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



 # Solo admins pueden validar

class ValidarRecargaUSDTView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, recarga_id, *args, **kwargs):
        try:
            recarga = RecargaUSDT.objects.get(id=recarga_id)

            if recarga.estado != 'pendiente':
                return Response({"message": "La recarga ya ha sido procesada."}, status=status.HTTP_400_BAD_REQUEST)

            # Validar la transacción en Solana
            wallet_address = settings.SOLANA_WALLET_ADDRESS
            validacion = validar_transaccion_solana(recarga.solana_tx_id, recarga.cantidad, wallet_address)

            if validacion["status"] == "success":
                # Actualizar cantidad si es diferente
                if recarga.cantidad != validacion['amount']:
                    recarga.cantidad = validacion['amount']
                
                # Aprobar la recarga en el sistema
                recarga.aprobar_recarga(admin=request.user)

                return Response({
                    "message": f"Recarga aprobada. Monto validado: {validacion['amount']} USDT.",
                    "admin_validador": request.user.username,
                    "fecha_validacion": recarga.fecha_validacion
                }, status=status.HTTP_200_OK)
            else:
                return Response({"message": validacion["message"]}, status=status.HTTP_400_BAD_REQUEST)

        except RecargaUSDT.DoesNotExist:
            return Response({"message": "Recarga no encontrada."}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"message": f"Error interno: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class ObtenerWalletUSDTView(APIView):
    """
    API para obtener la dirección de la wallet USDT actual y el tipo de red utilizado desde el backend.
    """
    def get(self, request, *args, **kwargs):
        wallet_address = settings.SOLANA_WALLET_ADDRESS  # Obtener desde settings.py
        network_type = settings.NETWORK_TYPE  # Obtener el tipo de red desde settings.py
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
