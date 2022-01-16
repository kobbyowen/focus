from typing import Dict, Text, Any
from django.contrib.auth.models import AbstractBaseUser
from rest_framework import serializers, status
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.conf import settings
from user_auth.models import User
from django.urls import reverse


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField(max_length=128)
    email = serializers.EmailField()
    name = serializers.CharField(max_length=512)
    last_login = serializers.DateTimeField()
    modified_at = serializers.DateTimeField()
    created_at = serializers.DateTimeField()
    _links = serializers.SerializerMethodField(read_only=True)

    def get__links(self, user: User):
        return {
            "user": reverse("user-crud", args=[user.pk]),
            "photos": "",
            "albums": ""
        }


class EditUserSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=128, required=False)
    email = serializers.EmailField(required=False)
    name = serializers.CharField(max_length=512, required=False)

    class Meta:
        model = User
        fields = ("username", "email", "name")
