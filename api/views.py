from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.utils import extend_schema
from . import serializers
from . import models

class CustomUserCreate(APIView):
    """
    Register new users to the system using valid credentails\n
    The account will be available after **activation** by the admins.
    """

    @extend_schema(
        request=serializers.CustomUserSerializer,
        responses={201: serializers.CustomUserSerializer, 400: None},
        tags=["user management"]
    )

    def post(self, request):
        serializer = serializers.CustomUserSerializer(data=request.data)
        
        if models.CustomUser.objects.filter(email=request.data.get('email')):
            return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)

        if models.CustomUser.objects.filter(username=request.data.get('username')):
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
        

        if serializer.is_valid():
            serializer.save()
            return Response({'user': serializer.data}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairView(TokenObtainPairView):
    @extend_schema(
        tags=["user management"]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class CustomTokenRefreshView(TokenRefreshView):
    @extend_schema(
        tags=["user management"]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class V1ApiGreet(APIView):
    
    @extend_schema(
        tags=["test"]
    )

    def get(self, request):
        """
        Simple `Hello World` message from the **/api/v1/info/** endpoint.
        """
        return Response({"message": "Hello, World from API version 1!"}, status=status.HTTP_200_OK)