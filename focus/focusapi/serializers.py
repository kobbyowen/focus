from typing import Dict, Text, Any
from django.contrib.auth.models import AbstractBaseUser
from rest_framework import serializers, status
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.conf import settings
from user_auth.models import User
from .models import Photo, Album
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
            "self": reverse("user-crud", args=[user.pk]),
            "photos": reverse("user-photos", args=[user.pk]),
            "albums": reverse("user-albums", args=[user.pk])
        }


class EditUserSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=128, required=False)
    email = serializers.EmailField(required=False)
    name = serializers.CharField(max_length=512, required=False)

    class Meta:
        model = User
        fields = ("username", "email", "name")


class PhotoSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(max_length=128, read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    modified_at = serializers.DateTimeField(read_only=True)
    created_by = serializers.SerializerMethodField(read_only=True)
    download_link = serializers.SerializerMethodField(read_only=True)

    def get_created_by(self, photo: Photo) -> Dict[Text, Any]:
        user = photo.created_by
        return {
            "id": user.id, "email": user.email, "username": user.username, "name": user.name, "user_link": reverse("user-crud", args=[user.pk])
        }

    def get_download_link(self, photo: Photo) -> Text:
        pk = photo.pk
        return reverse("download-photo", args=[pk])

    class Meta:
        model = Photo
        fields = ("id", "title", "file_path", "created_at",
                  "created_by", "modified_at")


class AlbumSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=512)
    created_at = serializers.DateTimeField(read_only=True)
    modified_at = serializers.DateTimeField(read_only=True)
    created_by = serializers.SerializerMethodField(read_only=True)
    photos = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Album

    def get_link(self, album: Album) -> Dict[Text, Any]:
        return {}

    def get_photos(self, album: Album) -> Text:
        return reverse("single-album-photos", args=[album.pk])

    def get_created_by(self, photo: Photo) -> Dict[Text, Any]:
        user = photo.created_by
        return {
            "id": user.id, "email": user.email, "username": user.username, "name": user.name, "user_link": reverse("user-crud", args=[user.pk])
        }
