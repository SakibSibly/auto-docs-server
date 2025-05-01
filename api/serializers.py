from rest_framework import serializers
from . import models


class CustomUserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=300)
    student_id = serializers.IntegerField()
    username = serializers.CharField(max_length=20)
    full_name = serializers.CharField(max_length=50)
    name_father = serializers.CharField(max_length=50)
    name_mother = serializers.CharField(max_length=50)
    session = serializers.CharField(max_length=20)
    blood_group = serializers.CharField(max_length=10)

    def create(self, validated_data):
        user = models.CustomUser(
            email=validated_data['email'],
            student_id=validated_data['student_id'],
            username=validated_data['username'],
            full_name=validated_data['full_name'],
            name_father=validated_data['name_father'],
            name_mother=validated_data['name_mother'],
            session=validated_data['session'],
            blood_group=validated_data['blood_group']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    
    def to_representation(self, instance):
        return {
            'email' : instance.email,
            'student_id' : instance.student_id,
            'username' : instance.username,
            'full_name' : instance.full_name,
            'name_father' : instance.name_father,
            'name_mother' : instance.name_mother,
            'session' : instance.session,
            'blood_group' : instance.blood_group
        }
