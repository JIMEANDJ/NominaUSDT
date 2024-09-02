from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Usuario, Empresa, Empleado, EmpleadoEmpresa, RecargaUSDT, OrdenDePago, ComprobanteDePago

admin.site.register(Usuario)
admin.site.register(Empresa)
admin.site.register(Empleado)
admin.site.register(EmpleadoEmpresa)
admin.site.register(RecargaUSDT)
admin.site.register(OrdenDePago)
admin.site.register(ComprobanteDePago)