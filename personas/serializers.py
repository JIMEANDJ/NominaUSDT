from rest_framework import serializers
from personas.models import RecargaUSDT, OrdenDePago, ComprobanteDePago

class RecargaUSDTSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecargaUSDT
        fields = '__all__'

class OrdenDePagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrdenDePago
        fields = '__all__'

class ComprobanteDePagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComprobanteDePago
        fields = '__all__'