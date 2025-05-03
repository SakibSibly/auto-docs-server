from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
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
            return Response({'detail': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)

        if models.CustomUser.objects.filter(student_id=request.data.get('student_id')):
            return Response({'detail': 'Student ID already exists'}, status=status.HTTP_400_BAD_REQUEST)
    
        role_id = request.data.get('role')
        role_instance = None

        if role_id is not None:
            try:
                role_instance = models.Role.objects.get(id=role_id)
            except models.Role.DoesNotExist:
                return Response({'detail': 'Invalid role ID'}, status=status.HTTP_400_BAD_REQUEST)
        
        if serializer.is_valid():
            user = serializer.save()
            if role_instance:
                user.role = role_instance
                user.save()

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

class V1CurrentUser(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["user management"]
    )

    def get(self, request):
        """
        Get the current user's information.
        """
        serializer = serializers.CustomUserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
