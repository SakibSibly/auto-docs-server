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
    Register new users to the system using valid credentails.\n
    The account will be available after **activation** by the admins.

    ## The minimum required fields for the JSON Request body are:\n
    1. **email**: The email address of the user.\n
    2. **password**: The password for the user account.\n
    3. **student_id**: The student ID of the user. e.g. 200104\n
    4. **role**: The role ID of the user. e.g. 1\n
    5. **session**: The session of the user. e.g. 2020-21\n
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
        tags=["authenticated user management"]
    )
    def get(self, request):
        """
        Get the current user's information.\n
        The user must be `authenticated` with valid **JWT token** to access this endpoint.\n
        """
        serializer = serializers.CustomUserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


    @extend_schema(
        request=serializers.CustomUserSerializer,
        responses={200: serializers.CustomUserSerializer, 400: None},
        tags=["authenticated user management"]
    )
    def put(self, request):
        """
        Update the current user's information.\n
        **Partial updates are allowed.**\n
        The user must be `authenticated` with valid **JWT token** to access this endpoint.\n
        """
        
        serializer = serializers.CustomUserSerializer(request.user, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(
        tags=["authenticated user management"]
    )
    def delete(self, request):
        """
        Delete the current user's account.\n
        The user must be `authenticated` with valid **JWT token** to access this endpoint.\n
        """
        user = request.user
        user.delete()
        return Response({"detail": "User account deleted successfully."}, status=status.HTTP_404_NOT_FOUND)