from django.urls import path
from .views import MyTokenObtainPairView, MyTokenRefreshView, EmpresaCreateAPIView, RegistroEmpleadoAPIView, UsuarioCreateAPIView

urlpatterns = [
    path('api/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', MyTokenRefreshView.as_view(), name='token_refresh'),
    path('api/registro-empresa/', EmpresaCreateAPIView.as_view(), name='empresa_create'),    
    path('api/registro-empleado/', RegistroEmpleadoAPIView.as_view(), name='create_empleado'),
    path('api/registro_usuario/', UsuarioCreateAPIView.as_view(), name='create_user'),
]
