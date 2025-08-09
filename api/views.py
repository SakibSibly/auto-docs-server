from django.utils import timezone
from django.shortcuts import render
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.utils import extend_schema, OpenApiParameter
from . import serializers
from . import models
from .utils.email_management import send_otp_email, send_link_email
from .utils.generate_serial import get_serial

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


class SendEmail(APIView):

    @extend_schema(
        tags=["user management"],
        parameters=[
            OpenApiParameter(
                name="method",
                type=str,
                location=OpenApiParameter.QUERY,
                description="The method of verification to be used. e.g. **otp**, **link**.",
                required=True
            )
        ],
        request=serializers.EmailSerializer,
        responses={
            200: {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "Email sent successfully"},
                }
                },
            400: {
                "type": "object",
                "properties": {
                    "details": {
                        "type": "string",
                        "details": "Error message"
                    }
                },
            }
        }
    )
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"error": "Email is required"}, status=400)
        
        if request.query_params.get('method') == 'link':
            send_link_email(email)
            return Response({"message": "Verification link sent"}, status=status.HTTP_200_OK)
            
        elif request.query_params.get('method') == 'otp':
            send_otp_email(email)
            return Response({"message": "OTP sent"}, status=status.HTTP_200_OK)


class VerifyEmail(APIView):

    @extend_schema(
        tags=["user management"],
        parameters=[
            OpenApiParameter(
                name="method",
                type=str,
                location=OpenApiParameter.QUERY,
                description="The method of verification to be used. e.g. **otp**, **link**.",
                required=True
            ),
            OpenApiParameter(
                name="email",
                type=str,
                location=OpenApiParameter.QUERY,
                description="The email of the user.",
                required=True
            ),
            OpenApiParameter(
                name="unique_id",
                type=str,
                location=OpenApiParameter.QUERY,
                description="The unique session ID for the OTP.",
                required=True
            ),
        ],
        responses={
            200: None,
            400: None
        }
    )
    def get(self, request):
        email = request.query_params.get('email')

        if not email:
            return Response({"details": "Email is required"}, status=400)

        if request.query_params.get('method') == 'link':
            unique_id = request.query_params.get('unique_id')
            if not unique_id:
                return Response({"details": "Unique ID is required"}, status=400)

            try:
                link_obj = models.EmailLink.objects.get(session_id=unique_id, email=email)
            except models.EmailLink.DoesNotExist:
                return Response({"details": "Invalid or expired link"}, status=400)

            if link_obj.is_expired():
                link_obj.is_verified = True
                link_obj.save()
                return render(request, 'pages/verification_expired.html', status=status.HTTP_400_BAD_REQUEST)
            
            # Mark the link as verified
            link_obj.is_verified = True
            link_obj.save()
            
            # Activate the account
            with transaction.atomic():
                models.CustomUser.objects.filter(email=email).update(is_active=True)

            return render(request, 'pages/email_verification.html', context={'user': request.user})
        
        elif request.query_params.get('method') == 'otp':
            otp = request.query_params.get('unique_id')
            if not otp:
                return Response({"details": "OTP is required"}, status=400)

            try:
                otp_obj = models.OTP.objects.filter(email=email, otp_code=otp, is_verified=False).latest('created_at')
            except models.OTP.DoesNotExist:
                return Response({"details": "Invalid OTP"}, status=400)

            if otp_obj.is_expired():
                otp_obj.is_verified = True
                otp_obj.save()
                return Response({"details": "OTP expired"}, status=400)

            # Mark the OTP as verified
            otp_obj.is_verified = True
            otp_obj.save()

            return Response({"message": "OTP verified successfully"})


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
                name="type",
                type=str,
                location=OpenApiParameter.QUERY,
                description="The role of the user. e.g. **alumni**, **student**.",
                required=False
            ),
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
            200: {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "email": {"type": "string", "description": "User email."},
                        "student_id": {"type": "integer", "description": "User student ID."},
                        "department": {"type": "integer", "description": "User department."},
                        "mobile_number": {"type": "string", "description": "User mobile number."},
                        "full_name": {"type": "string", "description": "User full name."},
                        "session": {"type": "string", "description": "User session."},
                        "role": {"type": "integer", "description": "User role."},
                        "user_photo": {"type": "string", "description": "User photo url."}
                    }
                }
            },
            400: {
                "type": "object",
                "properties": {
                    "detail": {"type": "string", "description": "Error message."}
                }
            },
        },
        request=None,
    )
    def get(self, request):
        """
        See user account status who applied for account creation.\n
        ## Optional query parameters:\n
        1. **status**: Filter requests by status.\n
        2. **type**: Filter requests by user type.\n
        3. **user_id**: Filter requests by user ID.\n
        ## Supported status values are:\n
        1. **all**: Show all user requests.\n
        2. **pending**: Show only pending user requests.\n
        3. **verified**: Show only verified user requests.\n
        4. **rejected**: Show only rejected user requests.\n
        ## Note:\n
        1. If no query parameters are provided, it will return all user requests who are alumni and students only.\n
        2. The user must be `authenticated` with valid **JWT token** with admin account to access this endpoint.\n
        """

        user_requests = models.CustomUser.objects.none()

        if request.query_params.get('status') == 'all':
            user_requests = models.CustomUser.objects.all()
        elif request.query_params.get('status') == 'pending':
            user_requests = models.CustomUser.objects.filter(is_active=False)
        elif request.query_params.get('status') == 'verified':
            user_requests = models.CustomUser.objects.filter(is_active=True)
        elif request.query_params.get('status') == 'rejected':
            return Response({"detail": "Needs to implement the feature!"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            user_requests = models.CustomUser.objects.all()
        

        if request.query_params.get('type') == 'alumni':
            user_requests = user_requests.filter(role__name='Alumni')
        elif request.query_params.get('type') == 'student':
            user_requests = user_requests.filter(role__name='Student')
        else:
            user_requests = user_requests.filter(role__name__in=['Alumni', 'Student'])
        
        if request.query_params.get('user_id'):
            try:
                user_id = int(request.query_params.get('user_id'))
                user_requests = user_requests.filter(student_id=user_id)
            except ValueError:
                return Response({"detail": "Invalid user ID provided."}, status=status.HTTP_400_BAD_REQUEST)
        
        if not user_requests:
            return Response({"detail": "No user requests found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer1 = serializers.CustomUserSerializer(user_requests, many=True)
        if not serializer1.data:
            return Response({"detail": "No user requests found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer2 = serializers.AccountRequestSerializer(user_requests, many=True)

        return Response(serializer2.data, status=status.HTTP_200_OK)


class V1ServicesOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["admin role permissions"],
        responses={
            200: {
                "type": "object",
                "properties": {
                    "total": {"type": "integer", "description": "Total number of service requests."},
                    "pending": {"type": "integer", "description": "Number of pending service requests."},
                    "students": {"type": "integer", "description": "Number of student service requests."},
                    "alumni": {"type": "integer", "description": "Number of alumni service requests."},
                    "revenue": {"type": "integer", "description": "Estimated revenue from accepted service requests."}
                }
            },
            400: {
                "type": "object",
                "properties": {
                    "detail": {"type": "string", "description": "Error message."}
                }
            },
        },
        request=None,
    )
    def get(self, request):
        """
        Get the overview of all services requested by users.\n
        The user must be `authenticated` with valid **JWT token** with admin account to access this endpoint.\n
        """
        services = models.ServiceRequest.objects.all()
        users = models.CustomUser.objects.all()
        
        if not services:
            return Response({"detail": "No services found."}, status=status.HTTP_404_NOT_FOUND)
        
        total = services.count()
        pending = services.filter(status__name='Pending').count()
        students = users.filter(role__name='Student').count()
        alumni = users.filter(role__name='Alumni').count()
        revenue = services.filter(status__name='Accepted').count() * 100 # Will have to fix later

        overview = {
            "total": total,
            "pending": pending,
            "students": students,
            "alumni": alumni,
            "revenue": revenue
        }

        serializer = serializers.ServiceSerializer(overview)

        if not serializer.data:
            return Response({"detail": "No services overview found."}, status=status.HTTP_404_NOT_FOUND)
        
        return Response(serializer.data, status=status.HTTP_200_OK)


class V1DepartmentView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["admin role permissions"],
        parameters=[
            OpenApiParameter(
                name="code",
                type=int,
                location=OpenApiParameter.QUERY,
                description="The code of the department. e.g. **1**, **2**.",
                required=False
            ),
        ],
        responses={
            200: serializers.DepartmentSerializer(many=True),
            400: {
                "type": "object",
                "properties": {
                    "detail": {"type": "string", "description": "Error message."}
                }
            },
        },
        request=None,
    )
    def get(self, request):
        """
        Get the list of all departments.\n

        ## Optional query parameter:\n
        1. **code**: Filter departments by code.\n
        ## Note:\n
        1. If no query parameter is provided, it will return all departments.\n
        2. The user must be `authenticated` with valid **JWT token** with admin account to access this endpoint.\n
        """
        departments = models.Department.objects.order_by('code')

        dept_code = request.query_params.get('code')

        if dept_code:
            try:
                department = departments.get(code=dept_code)
                
                if not department:
                    return Response({"detail": "Department not found."}, status=status.HTTP_404_NOT_FOUND)
                
                serializer = serializers.DepartmentSerializer(department)
                return Response(serializer.data, status=status.HTTP_200_OK)
            
            except models.Department.DoesNotExist:
                return Response({"detail": "Department not found."}, status=status.HTTP_404_NOT_FOUND)
        
        if not departments:
            return Response({"detail": "No departments found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = serializers.DepartmentSerializer(departments, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    @extend_schema(
        request=serializers.DepartmentSerializer,
        responses={201: serializers.DepartmentSerializer, 400: None},
        tags=["admin role permissions"]
    )
    def post(self, request):
        """
        Create a new department.\n
        The user must be `authenticated` with valid **JWT token** with admin account to access this endpoint.\n
        """
        serializer = serializers.DepartmentSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                department = serializer.save()
                department.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @extend_schema(
        request=serializers.DepartmentSerializer,
        responses={201: serializers.DepartmentSerializer, 400: None},
        tags=["admin role permissions"]
    )
    def put(self, request):
        """
        Update the department information.\n
        The user must be `authenticated` with valid **JWT token** with admin account to access this endpoint.\n
        """
        dept = models.Department.objects.filter(code=request.data.get('code')).first()
        if not dept:
            return Response({"detail": "Department not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = serializers.DepartmentSerializer(dept, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    @extend_schema(
        request=serializers.DepartmentSerializer,
        parameters=[
            OpenApiParameter(
                name="code",
                type=int,
                location=OpenApiParameter.QUERY,
                description="The code of the department. e.g. **1**, **2**.",
                required=False
            ),
        ],
        responses={200: {
            "type": "object",
            "properties": {
                "detail": {"type": "string", "description": "Success message."}
            }
        }, 400: {
            "type": "object",
            "properties": {
                "detail": {"type": "string", "description": "Error message."}
            }
        }},
        tags=["admin role permissions"]
    )
    def delete(self, request):
        """
        Delete a department.\n
        The user must be `authenticated` with valid **JWT token** with admin account to access this endpoint.\n
        """

        dept = models.Department.objects.filter(code=request.query_params.get('code')).first()
        
        if not dept:
            return Response({"detail": "Department not found."}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            dept.delete()
            return Response({"detail": "Department deleted successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class V1UserDetail(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["admin role permissions"],
        parameters=[
            OpenApiParameter(
                name="is_eligible",
                type=str,
                location=OpenApiParameter.QUERY,
                description="The eligibility status of user request. e.g. **True**, **False**.",
                required=False
            )
        ],
        responses={
            200: {
                "type": "object",
                "properties": {
                    "email": {"type": "string", "description": "User email."},
                    "student_id": {"type": "integer", "description": "User student ID."},
                    "student_reg": {"type": "integer", "description": "User student registration number."},
                    "gender": {"type": "integer", "description": "User gender"},
                    "department": {"type": "integer", "description": "User department."},
                    "mobile_number": {"type": "string", "description": "User mobile number."},
                    "date_of_birth": {"type": "string", "format": "date", "description": "User date of birth."},
                    "role": {"type": "integer", "description": "User role."},
                    "full_name": {"type": "string", "description": "User full name."},
                    "name_father": {"type": "string", "description": "User father's name."},
                    "name_mother": {"type": "string", "description": "User mother's name."},
                    "session": {"type": "string", "description": "User session."},
                    "passed_year": {"type": "string", "description": "User passed year."},
                    "cgpa": {"type": "number", "format": "float", "description": "User CGPA."},
                    "blood_group": {"type": "string", "description": "User blood group."},
                    "user_photo": {"type": "string", "description": "User photo URL."}
                }
            },
            404: {
                "type": "object",
                "properties": {
                    "detail": {"type": "string", "description": "Error message."}
                }
            }},
        request=None,
    )
    def get(self, request, student_id):
        """
        Get the details of a user by their ID.\n
        The user must be `authenticated` with valid **JWT token** to access this endpoint.\n
        """
        eligibility_status = request.query_params.get('is_eligible')

        if eligibility_status is not None:
            if eligibility_status == "False":
                with transaction.atomic():
                    models.CustomUser.objects.filter(student_id=student_id).update(is_rejected=True)
                return Response({'details': 'User account rejected!'})
            elif eligibility_status == "True":
                with transaction.atomic():
                    models.CustomUser.objects.filter(student_id=student_id).update(is_eligible=True)
                return Response({'details': 'User account approved'})



        try:
            user = models.CustomUser.objects.get(student_id=student_id)
            serializer = serializers.CustomUserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except models.CustomUser.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)


class SerialNumberGenarator(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["authenticated user management"],
        parameters=[
            OpenApiParameter(
                name="doc_type",
                type=str,
                location=OpenApiParameter.QUERY,
                description="The documnet type. e.g. **certificate**, **testimonial**",
                required=True
            )
        ],
        responses={
            200: {
                "type": "object",
                "properties": {
                    "student_id": {"type": "integer", "description": "The studnet id of the user"},
                    "serial": {"type": "string", "description": "The generated serial number"}
                }
            },
            404: {
                "type": "object",
                "properties": {
                    "detail": {"type": "string", "description": "Error message."}
                }
            }},
        request=None,
    )
    def get(self, request):
        """
        Get the serial number for a requested document.\n
        The user must be `authenticated` with valid **JWT token** to access this endpoint.\n

        **Supported parameters type are:**
        1. **certificate**
        2. **testimonial**
        3. **appreared**
        """
        
        if not request.user.is_eligible:
            return Response({"detail": "You're not eligible to make this request"}, status=status.HTTP_400_BAD_REQUEST)
        
        doc_type = request.query_params.get('doc_type')
        if doc_type == None:
            return Response({"detail": "document type is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            "student_id": request.user.student_id,
            "serial": get_serial(request.user, doc_type)
        }, status=status.HTTP_200_OK)
