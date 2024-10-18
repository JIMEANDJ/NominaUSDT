from rest_framework import serializers
from .models import RecargaUSDT, Empresa,  Empleado, ComprobanteDePago

class RecargaUSDTSerializer(serializers.ModelSerializer):
    empresa = serializers.SlugRelatedField(slug_field='nombre', queryset=Empresa.objects.all())
    admin_validador = serializers.StringRelatedField(read_only=True)  # Para mostrar el nombre del admin que validó
    fecha_validacion = serializers.DateTimeField(read_only=True)

    class Meta:
        model = RecargaUSDT
        fields = ['empresa', 'cantidad', 'solana_tx_id', 'estado', 'fecha', 'admin_validador', 'fecha_validacion']
        read_only_fields = ['estado', 'fecha', 'admin_validador', 'fecha_validacion']




class AprobarRecargaSerializer(serializers.Serializer):
    
    solicitud_id = serializers.IntegerField()
    accion = serializers.ChoiceField(choices=[('aprobar', 'Aprobar'), ('rechazar', 'Rechazar')])

    def validate_solicitud_id(self, value):
        try:
            recarga = RecargaUSDT.objects.get(id=value)
            if recarga.estado != 'pendiente':
                raise serializers.ValidationError("La solicitud ya ha sido procesada.")
            return value
        except RecargaUSDT.DoesNotExist:
            raise serializers.ValidationError("Solicitud no encontrada.")

    def validate(self, data):
        return data



class OrdenDePagoSerializer(serializers.ModelSerializer):
    comprobante_url = serializers.SerializerMethodField()

    class Meta:
        model = OrdenDePago
        fields = ['empresa', 'empleado', 'cantidad_usdt', 'cantidad_cop', 'comprobante_url']

    def get_comprobante_url(self, obj):
        if obj.comprobante:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.comprobante.archivo.url)
        return None


    class ComprobanteDePagoSerializer(serializers.ModelSerializer):
        class Meta:
            model = ComprobanteDePago
            fields = ['orden_de_pago', 'archivo']