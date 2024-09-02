# login/serializers.py

from rest_framework import serializers
from personas.models import Empresa, Empleado  # Ajusta la ruta de importación

class EmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empresa
        fields = '__all__'

class EmpleadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empleado
        fields = '__all__'