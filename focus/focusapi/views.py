from typing import Text, Dict, Any
import os
import uuid
from time import time
from rest_framework.views import APIView
from rest_framework import status
from .serializers import UserSerializer, EditUserSerializer, PhotoSerializer, AlbumSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from django.http import HttpResponse
from user_auth.models import User
from .models import Photo, Album
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.parsers import FileUploadParser
from django.conf import settings
from focus.errors import *
from django.shortcuts import get_object_or_404


def _get_error_response(code: int, message: Text, data: Any, **kwargs) -> Response:
    return Response({
        "error_code": code, "error_message": message, "data": data
    }, status=kwargs.get("status", status.HTTP_400_BAD_REQUEST))


def _get_success_response(data: Any, **kwargs: Dict[Text, Any]) -> Response:

    return Response({
        "error_code": SUCCESS_CODE, "error_message": SUCCESS_MESSAGE, "data": data
    }, status=kwargs.get("status", status.HTTP_200_OK))


def get_file_path(filename: Text) -> Text:
    ext = filename.split('.')[-1]
    name = f"{str(uuid.uuid4())}-{hex(int(time()))[:2]}"
    filename = f"{name}.{ext}"
    if not os.path.exists(settings.UPLOAD_DIR):
        try:
            os.mkdir(settings.UPLOAD_DIR)
        except OSError:
            # fallback to current directory instead of failing the
            return filename
    return os.path.join(settings.UPLOADS_DIR, filename)


class ListUsersView(APIView):
    permission_classes = [IsAdminUser]
    serializer_class = UserSerializer

    def get(self, request: Request) -> Response:

        users = User.objects.all()
        serialized = self.serializer_class(users, many=True)
        return _get_success_response(serialized.data)


class UserView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def _get_user(self, pk: int) -> Response:
        user = get_object_or_404(User, pk=pk)
        serialized = self.serializer_class(user)
        return _get_success_response(serialized.data)

    def _edit_user(self, user: User, data: Dict[Text, Any]) -> None:
        if data.get("email"):
            if User.objects.filter(email=data.get("email")).first() is not None:
                return None

        if data.get("username"):
            if User.objects.filter(email=data.get("username")).first() is not None:
                return None

        user.email = data.get("email", user.email)
        user.username = data.get("username", user.username)
        user.name = data.get("name", user.name)

        user.save()
        return user

    def get(self, request: Request, pk: int) -> Response:
        if not request.user.is_admin and request.user.pk != pk:
            return _get_error_response(FORBIDDEN_CODE, FORBIDDEN_MESSAGE, None, status=status.HTTP_403_FORBIDDEN)

        return self._get_user(pk)

    def delete(self, request: Request, pk: int) -> Response:
        if not request.user.is_admin:
            return _get_error_response(FORBIDDEN_CODE, FORBIDDEN_MESSAGE, None, status=status.HTTP_403_FORBIDDEN)
        user = get_object_or_404(User, pk=pk)
        user.delete()
        return _get_success_response({})

    def put(self, request: Request, pk: int) -> Response:
        if request.user.pk != pk:
            return _get_error_response(FORBIDDEN_CODE, FORBIDDEN_MESSAGE, status=status.HTTP_403_FORBIDDEN)
        user = get_object_or_404(User, pk=pk)
        request.data["user"] = user
        serializer = EditUserSerializer(data=request.data)
        if not serializer.is_valid():
            return _get_error_response(INVALID_LOGIN_CREDENTIALS_CODE, INVALID_LOGIN_CREDENTIALS_MESSAGE, serializer.errors)
        if self._edit_user(user, request.data) is None:
            return _get_error_response(DUPLICATE_CODE, "A user already exists with same email or username", data)
        return self._get_user(pk)


class AllPhotosView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PhotoSerializer
    parser_class = (FileUploadParser,)

    def _process_upload_request(self, file, data) -> Response:
        if not file.content_type.startswith("image"):
            return _get_error_response(MISSING_PARAMETER_CODE, MISSING_PARAMETER_MESSAGE, {"detail": "file parameter should be an image"})
        name = data.get("title", file.name)
        file_path = get_file_path(file.name)
        with open(file_path, "wb") as uploaded_file:
            uploaded_file.write(file.read())
        return (name, file_path)

    def get(self, request: Request) -> Response:
        photo = Photo.objects.all()
        serialized = self.serializer_class(photo, many=True)
        return _get_success_response(serialized.data)

    def post(self, request: Request) -> Response:
        if "file" not in request.data:
            return _get_error_response(MISSING_PARAMETER_CODE, MISSING_PARAMETER_MESSAGE, {"detail": "file parameter is missing"})
        file = request.data["file"]
        name, file_path = self._process_upload_request(file, request.data)
        photo = Photo.objects.create(
            created_by=request.user, title=name, file_path=file_path)
        photo.save()
        serialized = self.serializer_class(photo)
        return _get_success_response(serialized.data, status=status.HTTP_201_CREATED)


class MyProfileView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get(self, request: Request) -> Response:
        user = request.user
        serialized = self.serializer_class(user)
        return _get_success_response(serialized.data)


class PhotoDownloadView(APIView):
    permission_classes = [AllowAny]

    def get(self, request: Request, pk: int) -> Response:
        photo = get_object_or_404(Photo, pk=pk)
        file_path = photo.file_path
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                response = HttpResponse(
                    f.read(), content_type=photo.mimetype)
                response['Content-Disposition'] = 'inline; filename=' + \
                    os.path.basename(file_path)
                return response
        return _get_error_response(RESOURCE_NOT_FOUND_CODE, RESOURCE_NOT_FOUND_MESSAGE, data, status=status.HTTP_404_NOT_FOUND)


class UserPhotosView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PhotoSerializer

    def get(self, request: Request, pk: int) -> Response:
        user = get_object_or_404(User, pk=pk)
        photos = Photo.objects.filter(created_by=user.pk).all()
        serialized = self.serializer_class(photos, many=True)
        return _get_success_response(serialized.data)


class UserAlbumsView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AlbumSerializer

    def get(self, request: Request, pk: int) -> Response:
        user = get_object_or_404(User, pk=pk)
        albums = Album.objects.filter(created_by=user.pk).all()
        serialized = self.serializer_class(albums, many=True)
        return _get_success_response(serialized.data)


class PhotoView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PhotoSerializer

    def get(self, request: Request, pk: int) -> Response:
        photo = get_object_or_404(Photo, pk=pk)
        serialized = self.serializer_class(photo)
        return _get_success_response(serialized.data)

    def put(self, request: Request, pk: int) -> Response:
        photo = get_object_or_404(Photo, pk=pk)
        if photo.created_by.pk != request.user.pk:
            return _get_error_response(FORBIDDEN_CODE, FORBIDDEN_MESSAGE, None, status=status.HTTP_403_FORBIDDEN)
        title = request.data.get("title", photo.title)
        photo.title = title
        photo.save()
        serialized = self.serializer_class(photo)
        return _get_success_response(serialized.data)

    def delete(self, request: Request, pk: int) -> Response:
        photo = get_object_or_404(Photo, pk=pk)
        if photo.created_by.pk != request.user.pk:
            return _get_error_response(FORBIDDEN_CODE, FORBIDDEN_MESSAGE, None, status=status.HTTP_403_FORBIDDEN)
        photo.delete()
        return _get_success_response({})


class AlbumView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AlbumSerializer

    def get(self, request: Request) -> Response:
        if not request.user.is_admin:
            return _get_error_response(FORBIDDEN_CODE, FORBIDDEN_MESSAGE, None, status=status.HTTP_403_FORBIDDEN)
        albums = Album.objects.all()
        serialized = self.serializer_class(albums, many=True)
        return _get_success_response(serialized.data)

    def post(self, request: Request) -> Response:
        serialized = self.serializer_class(Album, data=request.data)
        if not serialized.is_valid():
            return _get_error_response(MISSING_PARAMETER_CODE, MISSING_PARAMETER_MESSAGE, serialized.errors)
        album = Album.objects.create(
            name=request.data["name"], created_by=request.user)
        album.save()
        return _get_success_response(self.serializer_class(album).data, status=status.HTTP_201_CREATED)


class SingleAlbumView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AlbumSerializer

    def get(self, request: Request, pk: int) -> Response:
        album = get_object_or_404(Album, pk=pk)
        if album.created_by.pk != request.user.pk:
            return _get_error_response(FORBIDDEN_CODE, FORBIDDEN_MESSAGE, None, status=status.HTTP_403_FORBIDDEN)
        serialized = self.serializer_class(album)
        return _get_success_response(serialized.data)

    def delete(self, request: Request, pk: int) -> Response:
        album = get_object_or_404(Album, pk=pk)
        if album.created_by.pk != request.user.pk:
            return _get_error_response(FORBIDDEN_CODE, FORBIDDEN_MESSAGE, None, status=status.HTTP_403_FORBIDDEN)
        album.delete()
        return _get_success_response({})

    def put(self, request: Request, pk: int) -> Response:
        album = get_object_or_404(Album, pk=pk)
        serialized = self.serializer_class(Album, data=request.data)
        if not serialized.is_valid():
            return _get_error_response(MISSING_PARAMETER_CODE, MISSING_PARAMETER_MESSAGE, serialized.errors)
        album.name = request.data["name"]
        album.save()
        return _get_success_response(self.serializer_class(album).data, status=status.HTTP_200_OK)


class SingleAlbumPhotosView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AlbumSerializer

    def get(self, request: Request, pk: int) -> Response:
        album: Album = get_object_or_404(Album, pk=pk)
        if album.created_by.pk != request.user.pk:
            return _get_error_response(FORBIDDEN_CODE, FORBIDDEN_MESSAGE, None, status=status.HTTP_403_FORBIDDEN)
        print(album.photos)
        serialized = PhotoSerializer(album.photos.all(), many=True)
        return _get_success_response(serialized.data)

    def put(self, request: Request, pk: int) -> Response:
        album: Album = get_object_or_404(Album, pk=pk)
        if request.user.pk != album.created_by.pk:
            return _get_error_response(FORBIDDEN_CODE, FORBIDDEN_MESSAGE, None, status=status.HTTP_403_FORBIDDEN)
        data = request.data["photo_ids"]
        operation = request.data.get("operation", "add").lower()

        if not isinstance(data, list):
            return _get_error_response(MISSING_PARAMETER_CODE, MISSING_PARAMETER_MESSAGE, {"detail": "Expected photo_ids to be an array of ints"})
        for pk in data:
            try:
                photo = Photo.objects.get(id=pk)

                if operation == "remove":
                    album.photos.remove(photo)
                else:
                    album.photos.add(photo)
            except Photo.DoesNotExist:
                album = album.__class__._default_manager.get(pk=album.pk)
                return _get_error_response(RESOURCE_NOT_FOUND_CODE, RESOURCE_NOT_FOUND_MESSAGE, {"detail": f"photo with id {pk!r} cannot be found"}, status=status.HTTP_400_BAD_REQUEST)

        album.save()
        return _get_success_response(self.serializer_class(album).data, status=status.HTTP_200_OK)


class AlbumPhotosView(APIView):

    def delete(self, request: Request, album_id: int, photo_id: int) -> Response:
        album: Album = get_object_or_404(Album, pk=album_id)
        photo: Photo = album.photos.filter(id=photo_id).first()
        if photo is None:
            return _get_error_response(RESOURCE_NOT_FOUND_CODE, RESOURCE_NOT_FOUND_MESSAGE, {"detail": f"photo with id {photo_id!r} cannot be found in album"}, status=status.HTTP_404_NOT_FOUND)
        album.photos.remove(photo)
        album.save()
        return _get_success_response({})
