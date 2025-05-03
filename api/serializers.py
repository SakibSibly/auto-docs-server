from rest_framework import serializers
from . import models


class CustomUserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=300)
    student_id = serializers.IntegerField()
    mobile_number = serializers.CharField(max_length=15, required=False, allow_blank=True)
    date_of_birth = serializers.DateField(required=False, allow_null=True)
    role = serializers.IntegerField()
    full_name = serializers.CharField(max_length=50, required=False, allow_blank=True)
    name_father = serializers.CharField(max_length=50, required=False, allow_blank=True)
    name_mother = serializers.CharField(max_length=50, required=False, allow_blank=True)
    session = serializers.CharField(max_length=20)
    blood_group = serializers.CharField(max_length=10, required=False, allow_blank=True)

    def create(self, validated_data):
        user = models.CustomUser(
            email=validated_data.get('email', ""),
            student_id=validated_data.get('student_id', ""),
            mobile_number=validated_data.get('mobile_number', ""),
            date_of_birth=validated_data.get('date_of_birth', None),
            role_id=validated_data.get('role', ""),
            full_name=validated_data.get('full_name', ""),
            name_father=validated_data.get('name_father', ""),
            name_mother=validated_data.get('name_mother', ""),
            session=validated_data.get('session', ""),
            blood_group=validated_data.get('blood_group', "")
        )
        user.set_password(validated_data.get('password', ""))
        user.save()
        return user

    
    def to_representation(self, instance):
        return {
            'email' : instance.email,
            'student_id' : instance.student_id,
            'mobile_number' : instance.mobile_number,
            'date_of_birth' : instance.date_of_birth,
            'role' : instance.role_id,
            'full_name' : instance.full_name,
            'name_father' : instance.name_father,
            'name_mother' : instance.name_mother,
            'session' : instance.session,
            'blood_group' : instance.blood_group
        }
