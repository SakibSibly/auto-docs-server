from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.utils import extend_schema, OpenApiParameter
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
    4. **department**: The department ID of the user. e.g. 1\n
    5. **role**: The role ID of the user. e.g. 1\n
    6. **session**: The session of the user. e.g. 2020-21\n
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
    
        # Custom logic to handle foreign keys

        role_id = request.data.get('role')
        role_instance = None

        if role_id is not None:
            try:
                role_instance = models.Role.objects.get(id=role_id)
            except models.Role.DoesNotExist:
                return Response({'detail': 'Invalid role ID'}, status=status.HTTP_400_BAD_REQUEST)
        
        department_id = request.data.get('department')
        department_instance = None

        if department_id is not None:
            try:
                department_instance = models.Department.objects.get(id=department_id)
            except models.Department.DoesNotExist:
                return Response({'detail': 'Invalid department ID'}, status=status.HTTP_400_BAD_REQUEST)
            
        gender_id = request.data.get('gender')
        gender_instance = None

        if gender_id is not None:
            try:
                gender_instance = models.Gender.objects.get(id=gender_id)
            except models.Gender.DoesNotExist:
                return Response({'detail': 'Invalid gender ID'}, status=status.HTTP_400_BAD_REQUEST)
        

        if serializer.is_valid():
            user = serializer.save()
            if role_instance:
                user.role = role_instance
            if department_instance:
                user.department = department_instance
            if gender_instance:
                user.gender = gender_instance
            
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


class V1HandleServiceView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["service management"],
        parameters=[
            OpenApiParameter(
                name="doc_type",
                type=str,
                location=OpenApiParameter.QUERY,
                description="The type of document requested. e.g. **testimonial**, **certificate**, **transcript**.",
                required=True
            )
        ],
        responses={
            200: None,
            400: None,
        },
        request=None,
    )
    def get(self, request):
        """
        Request for services with the query parameter `doc_type`\n
        ## Supported document types are:\n
        1. **testimonial**\n
        2. **certificate**\n
        3. **transcript**\n
    
        The user must be `authenticated` with valid **JWT token** to access this endpoint.\n
        """

        doc_type = request.query_params.get('doc_type')

        if doc_type == "testimonial":
            # Handle the request for testimonial
            return Response({"message": "Testimonial request received."}, status=status.HTTP_200_OK)
        elif doc_type == "certificate":
            # Handle the request for certificate
            return Response({"message": "Certificate request received."}, status=status.HTTP_200_OK)
        elif doc_type == "transcript":
            # Handle the request for transcript
            return Response({"message": "Transcript request received."}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Invalid document request received!"}, status=status.HTTP_400_BAD_REQUEST)
        
class V1UserRequestHandleView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["admin role permissions"],
        parameters=[
            OpenApiParameter(
                name="status",
                type=str,
                location=OpenApiParameter.QUERY,
                description="The user account status. e.g. **all**, **pending**.",
                required=False
            ),
            OpenApiParameter(
                name="user_id",
                type=int,
                location=OpenApiParameter.QUERY,
                description="The user ID to filter requests. e.g. **1**, **2**.",
                required=False
            )
        ],
        responses={
            200: None,
            400: None,
        },
        request=None,
    )
    def get(self, request):
        """
        See user account status who applied for account creation.\n
        ## Optional query parameters:\n
        1. **user_id**: Filter requests by user ID.\n
        2. **status**: Filter requests by status.\n
        ## Supported status values are:\n
        1. **all**: Show all user requests.\n
        2. **pending**: Show only pending user requests.\n
        3. **approved**: Show only approved user requests.\n
        4. **rejected**: Show only rejected user requests.\n
        ## Note:\n
        1. If no query parameters are provided, it will return all user requests.\n
        2. If `status` is provided, it will filter the requests based on the status.\n
        3. If `user_id` is provided, it will filter the requests based on the user ID.\n
        4. If both `status` and `user_id` are provided, it will filter the requests based on both parameters.\n
        5. The user must be `authenticated` with valid **JWT token** with admin account to access this endpoint.\n
        """

        # Implement logic to retrieve service requests based on the status and user_id query parameters
        return Response({"message": "User account request list retrieved."}, status=status.HTTP_200_OK)