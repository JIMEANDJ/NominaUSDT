from django.contrib import admin

# Register your models here.
from django.contrib import admin
from personas.models import  RecargaUSDT, OrdenDePago, ComprobanteDePago  # Ajusta la ruta de importación

'''admin.site.register(Empresa)
admin.site.register(Empleado
admin.site.register(EmpleadoEmpresa)'''
admin.site.register(RecargaUSDT)
admin.site.register(OrdenDePago)
admin.site.register(ComprobanteDePago)

'''Empresa, Empleado, EmpleadoEmpresa,'''