# login/urls.py

from django.urls import path
from .views import MyTokenObtainPairView, MyTokenRefreshView, EmpresaCreateAPIView, EmpleadoCreateAPIView


urlpatterns = [
    path('api/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', MyTokenRefreshView.as_view(), name='token_refresh'),
    path('api/empresa/', EmpresaCreateAPIView.as_view(), name='empresa_create'),
    path('api/empleado/', EmpleadoCreateAPIView.as_view(), name='empleado_create'),
]
