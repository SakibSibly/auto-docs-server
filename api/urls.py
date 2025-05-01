from django.urls import path
from . import views

urlpatterns = [
    path('v1/info/', views.V1ApiGreet.as_view(), name='note-list-create'),
]