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
    path('v1/email/', views.SendEmail.as_view(), name='send-email'),
    path('v1/email/verify/', views.VerifyEmail.as_view(), name='verify-email'),
    path('v1/users/me/', views.V1CurrentUser.as_view(), name='current-user'),
    path('v1/info/', views.V1ApiGreet.as_view(), name='hello-world-message'),
    path('v1/services/', views.V1HandleServiceView.as_view(), name='service-list'),
    path('v1/users/request/serial-number/', views.SerialNumberGenarator.as_view(), name='get-serial-number'),

    # API admin
    path('v1/admin/users/<int:student_id>/', views.V1UserDetail.as_view(), name='user-detail'),
    path('v1/admin/departments/', views.V1DepartmentView.as_view(), name='admin-department-list'),
    path('v1/admin/user-requests/', views.V1UserRequestHandleView.as_view(), name='admin-service-list'),
    path('v1/admin/services-overview/', views.V1ServicesOverviewView.as_view(), name='admin-services-overview'),
]