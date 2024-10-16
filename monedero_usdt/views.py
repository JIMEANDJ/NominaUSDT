from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RecargaUSDTSerializer
from personas.models import RecargaUSDT, Notificacion
import requests

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


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import AprobarRecargaSerializer
from .models import RecargaUSDT, Notificacion

class AprobarRecargaUSDTAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = AprobarRecargaSerializer(data=request.data)
        if serializer.is_valid():
            solicitud_id = serializer.validated_data['solicitud_id']
            accion = serializer.validated_data['accion']

            try:
                recarga = RecargaUSDT.objects.get(id=solicitud_id)
            except RecargaUSDT.DoesNotExist:
                return Response({"error": "Solicitud no encontrada."}, status=status.HTTP_404_NOT_FOUND)

            if accion == 'aprobar':
                recarga.aprobar_recarga()
                mensaje = f"Tu recarga de {recarga.cantidad} USDT ha sido aprobada."
                Notificacion.objects.create(usuario=recarga.empresa.admin_usuario, mensaje=mensaje)
                return Response({"mensaje": "Solicitud aprobada."}, status=status.HTTP_200_OK)

            elif accion == 'rechazar':
                recarga.rechazar_recarga()
                mensaje = f"Tu recarga de {recarga.cantidad} USDT ha sido rechazada."
                Notificacion.objects.create(usuario=recarga.empresa.admin_usuario, mensaje=mensaje)
                return Response({"mensaje": "Solicitud rechazada."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
