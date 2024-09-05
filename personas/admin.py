from django.contrib import admin

from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Empresa, Empleado, EmpleadoEmpresa

# Register your models here.

# Registrar el modelo Usuario con el administrador de usuarios personalizado
admin.site.register(Usuario, UserAdmin)

# Registrar el modelo Empresa
admin.site.register(Empresa)

#Registrar otros modelos si es necesario
admin.site.register(Empleado)
admin.site.register(EmpleadoEmpresa)