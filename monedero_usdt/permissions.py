from rest_framework.permissions import BasePermission

class AllowPartialAccess(BasePermission):
    """
    Permite acceso para funciones no críticas. Requiere autenticación completa para acciones críticas.
    """
    def has_permission(self, request, view):
        # Permite acceso si es un método GET o si el usuario está autenticado
        if request.method == 'GET' or request.user.is_authenticated:
            return True
        return False
