import os
from .models import CustomUser, File
from rest_framework import serializers
from ez_assignment.utils.helper import generate_signup_token

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'first_name', 'last_name', 'email', 'mobile', 'is_ops_user',)

class FileSerializer(serializers.ModelSerializer):
    filename = serializers.SerializerMethodField()
    class Meta:
        model = File
        fields = ('id', 'user', 'file_type','filename',)

    def get_filename(self, instance):
        return os.path.basename(instance.file.name) if instance.file.name else "None"

class ClientUserSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        validated_data.pop('user_permissions',None)
        validated_data.pop('groups',None)
        validated_data.pop('is_active',None)
        validated_data.pop('is_ops_user',None)
        instance = self.Meta.model(**validated_data)

        if password is not None:
            instance.set_password(password)
        instance.is_active=False
        token = generate_signup_token()
        instance.signup_token = token
        instance.is_ops_user = False
        instance.save()
        return instance
