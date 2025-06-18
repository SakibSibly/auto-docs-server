from rest_framework import serializers
from . import models


class CustomUserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=300)
    student_id = serializers.IntegerField()
    student_reg = serializers.IntegerField(required=False, allow_null=True)
    gender = serializers.IntegerField(required=False, allow_null=True)
    department = serializers.IntegerField()
    mobile_number = serializers.CharField(max_length=15, required=False, allow_blank=True)
    date_of_birth = serializers.DateField(required=False, allow_null=True)
    role = serializers.IntegerField()
    full_name = serializers.CharField(max_length=50, required=False, allow_blank=True)
    name_father = serializers.CharField(max_length=50, required=False, allow_blank=True)
    name_mother = serializers.CharField(max_length=50, required=False, allow_blank=True)
    session = serializers.CharField(max_length=20)
    passed_year = serializers.CharField(max_length=10, required=False, allow_blank=True)
    cgpa = serializers.FloatField(required=False, allow_null=True)
    blood_group = serializers.CharField(max_length=10, required=False, allow_blank=True)
    user_photo = serializers.CharField(required=False, allow_blank=True)

    def create(self, validated_data):
        user = models.CustomUser(
            email=validated_data.get('email', ""),
            student_id=validated_data.get('student_id', ""),
            student_reg=validated_data.get('student_reg', None),
            gender_id=validated_data.get('gender', None),
            department_id=validated_data.get('department', ""),
            mobile_number=validated_data.get('mobile_number', ""),
            date_of_birth=validated_data.get('date_of_birth', None),
            role_id=validated_data.get('role', ""),
            full_name=validated_data.get('full_name', ""),
            name_father=validated_data.get('name_father', ""),
            name_mother=validated_data.get('name_mother', ""),
            session=validated_data.get('session', ""),
            passed_year=validated_data.get('passed_year', ""),
            cgpa=validated_data.get('cgpa', None),
            blood_group=validated_data.get('blood_group', ""),
            user_photo=validated_data.get('user_photo', "")
        )
        user.set_password(validated_data.get('password', ""))
        user.save()
        return user
    
    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        instance.student_id = validated_data.get('student_id', instance.student_id)
        instance.student_reg = validated_data.get('student_reg', instance.student_reg)
        instance.gender_id = validated_data.get('gender', instance.gender)
        instance.department_id = validated_data.get('department', instance.department)
        instance.mobile_number = validated_data.get('mobile_number', instance.mobile_number)
        instance.date_of_birth = validated_data.get('date_of_birth', instance.date_of_birth)
        instance.role_id = validated_data.get('role', instance.role_id)
        instance.full_name = validated_data.get('full_name', instance.full_name)
        instance.name_father = validated_data.get('name_father', instance.name_father)
        instance.name_mother = validated_data.get('name_mother', instance.name_mother)
        instance.session = validated_data.get('session', instance.session)
        instance.passed_year = validated_data.get('passed_year', instance.passed_year)
        instance.cgpa = validated_data.get('cgpa', instance.cgpa)
        instance.blood_group = validated_data.get('blood_group', instance.blood_group)
        instance.user_photo = validated_data.get('user_photo', instance.user_photo)

        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
        
        instance.save()
        return instance

    
    def to_representation(self, instance):
        return {
            'email' : instance.email,
            'student_id' : instance.student_id,
            'student_reg' : instance.student_reg,
            'gender' : instance.gender_id,
            'department' : instance.department_id,
            'mobile_number' : instance.mobile_number,
            'date_of_birth' : instance.date_of_birth,
            'role' : instance.role_id,
            'full_name' : instance.full_name,
            'name_father' : instance.name_father,
            'name_mother' : instance.name_mother,
            'session' : instance.session,
            'passed_year' : instance.passed_year,
            'cgpa' : instance.cgpa,
            'blood_group' : instance.blood_group,
            'user_photo' : instance.user_photo
        }
