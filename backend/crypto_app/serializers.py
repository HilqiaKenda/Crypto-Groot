from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User


class UserSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = ["id", "username", "email"]


class RegisterUserSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = ["username", "email", "password"]
        extra_kwargs = {"password": {"write_only":True}}


class LoginSerializer(Serializer):
    username = serializers.CharField(max_length=100)
    # email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(**data)

        if user and user.is_active:
            return user
        
        raise serializers.ValidationError("Incorect credential!")