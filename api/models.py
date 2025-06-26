from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class RequestStatus(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class Document(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class Faculty(models.Model):
    name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class Department(models.Model):
    code = models.IntegerField(unique=True)
    name = models.CharField(max_length=100, unique=True)
    short_name = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True, blank=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Course(models.Model):
    course_code = models.CharField(max_length=100, unique=True)
    course_title = models.CharField(max_length=200)
    course_description = models.TextField(null=True, blank=True)
    dept_name = models.ForeignKey(Department, on_delete=models.CASCADE)
    course_credit = models.FloatField()

    def __str__(self):
        return self.course_code + ' - ' + self.course_title


class Gender(models.Model):
    name = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.name


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=300)
    student_id = models.IntegerField(unique=True)
    student_reg = models.IntegerField(null=True, blank=True)
    gender = models.ForeignKey(Gender, on_delete=models.CASCADE, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)
    mobile_number = models.CharField(max_length=15, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, null=True, blank=True)
    full_name = models.CharField(max_length=50, null=True, blank=True)
    name_father = models.CharField(max_length=50, null=True, blank=True)
    name_mother = models.CharField(max_length=50, null=True, blank=True)
    session = models.CharField(max_length=20)
    passed_year = models.CharField(max_length=10, null=True, blank=True)
    cgpa = models.FloatField(null=True, blank=True)
    blood_group = models.CharField(max_length=10, null=True, blank=True)
    user_photo = models.TextField(null=True, blank=True)

    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['student_id']

    def __str__(self):
        return str(self.student_id)


class OTP(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email + ' - ' + self.otp


class ServiceRequest(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    request_doc = models.ForeignKey(Document, on_delete=models.CASCADE)
    status = models.ForeignKey(RequestStatus, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student} - {self.request_doc} - {self.status}"


class StudentRecord(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    semester = models.CharField(max_length=10)
    credit = models.FloatField()
    year = models.IntegerField()
    gpa = models.FloatField()

    def __str__(self):
        return f"{self.student} - {self.course.course_code} - {self.semester} - {self.year}"
