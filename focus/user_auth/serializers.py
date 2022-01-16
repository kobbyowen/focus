from typing import Dict, Text, Any
from datetime import datetime, timezone
import pytz
from django.contrib.auth.models import AbstractBaseUser
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from django.conf import settings
from django.urls import reverse
from .models import User


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=128, min_length=8, write_only=True)

    token = token = serializers.CharField(read_only=True, max_length=512)

    class Meta:
        model = User
        fields = ("name", "username", "email", "password", "token")

    def create(self, validated_data: Dict[Text, Any]) -> AbstractBaseUser:
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):

    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(max_length=128, write_only=True)

    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(max_length=255, read_only=True)
    token = serializers.CharField(max_length=255, read_only=True)
    expires = serializers.IntegerField(read_only=True)
    _links = serializers.SerializerMethodField(read_only=True)

    def get__links(self, user: User):
        return {
            "user": user["_links"]["user"],
        }

    def validate(self, data: Dict[Text, Any]) -> Dict[Text, Any]:

        email = data.get("email", None)
        password = data.get("password", None)

        if email is None:
            raise serializers.ValidationError(
                "An email address is required to log in.")

        if password is None:
            raise serializers.ValidationError(
                "A password is required to log in."
            )

        user: User = authenticate(username=email, password=password)

        if user is None:
            raise serializers.ValidationError(
                "A user with this email and password was not found."
            )
        user.last_login = datetime.now(pytz.utc)
        user.save()
        return {
            "expires": settings.TOKEN_LIEFTIME,
            "token": user.token,
            "id": user.pk,
            "_links": {
                "user":  reverse("user-crud", args=[user.pk])
            }
        }
