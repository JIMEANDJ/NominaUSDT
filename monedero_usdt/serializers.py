from rest_framework import serializers
from .models import RecargaUSDT, Empresa

class RecargaUSDTSerializer(serializers.ModelSerializer):
    empresa_nombre = serializers.CharField(write_only=True)  # Para recibir el nombre de la empresa en la solicitud

    class Meta:
        model = RecargaUSDT
        fields = ['id', 'empresa_nombre', 'cantidad', 'solana_tx_id', 'fecha', 'estado']
        read_only_fields = ['id', 'fecha', 'estado']

    def validate(self, data):
        empresa_nombre = data.get('empresa_nombre')
        solana_tx_id = data.get('solana_tx_id')

        # Verificar que la empresa exista
        try:
            empresa = Empresa.objects.get(nombre=empresa_nombre)
            data['empresa'] = empresa
        except Empresa.DoesNotExist:
            raise serializers.ValidationError("Empresa no encontrada.")

        # Verificar que el solana_tx_id sea único
        if RecargaUSDT.objects.filter(solana_tx_id=solana_tx_id).exists():
            raise serializers.ValidationError("El ID de transacción ya ha sido registrado.")

        return data

    def create(self, validated_data):
        empresa = validated_data.pop('empresa')
        recarga = RecargaUSDT.objects.create(empresa=empresa, **validated_data)
        return recarga


from rest_framework import serializers
from .models import RecargaUSDT

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


