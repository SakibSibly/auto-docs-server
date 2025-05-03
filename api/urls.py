from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from . import views

urlpatterns = [
    path('schemas/', SpectacularAPIView.as_view(), name="schemas"),
    path('schemas/docs', SpectacularSwaggerView.as_view(url_name="schemas")),

    path('token/', views.CustomTokenObtainPairView.as_view(), name='get-token'),
    path('token/refresh/', views.CustomTokenRefreshView.as_view(), name='refresh-token'),
    path('register/', views.CustomUserCreate.as_view(), name='register'),

    # API v1
    path('v1/users/me/', views.V1CurrentUser.as_view(), name='current-user'),
    path('v1/info/', views.V1ApiGreet.as_view(), name='hello-world-message'),
]