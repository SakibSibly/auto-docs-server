from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from . import views

urlpatterns = [
    path('schemas/', SpectacularAPIView.as_view(), name="schemas"),
    path('schemas/docs', SpectacularSwaggerView.as_view(url_name="schemas")),
    path('token/', TokenObtainPairView.as_view(), name='get-token'),
    path('token/refresh/', TokenRefreshView.as_view(), name='refresh-token'),
    path('register/', views.CustomUserCreate.as_view(), name='register'),
    path('v1/info/', views.V1ApiGreet.as_view(), name='note-list-create'),
]