from typing import Text, Dict, Any
from rest_framework.views import APIView
from rest_framework import status
from .serializers import UserSerializer, EditUserSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from user_auth.models import User
from rest_framework.response import Response
from rest_framework.request import Request
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
        user.email = data.get("email", user.email)
        user.username = data.get("username", user.username)
        user.name = data.get("name", user.name)

        user.save()

    def get(self, request: Request, pk: int) -> Response:
        if not request.user.is_admin and request.user.pk != pk:
            return _get_error_response(FORBIDDEN_CODE, FORBIDDEN_MESSAGE, None)

        return self._get_user(pk)

    def delete(self, request: Request, pk: int) -> Response:
        if not request.user.is_admin:
            return _get_error_response(FORBIDDEN_CODE, FORBIDDEN_MESSAGE, None)
        user = get_object_or_404(User, pk=pk)
        user.delete()
        return _get_success_response({})

    def put(self, request: Request, pk: int) -> Response:
        if request.user.pk != pk:
            return _get_error_response(FORBIDDEN_CODE, FORBIDDEN_MESSAGE, None)
        user = get_object_or_404(User, pk=pk)
        request.data["user"] = user
        serializer = EditUserSerializer(data=request.data)
        if not serializer.is_valid():
            return _get_error_response(INVALID_LOGIN_CREDENTIALS_CODE, INVALID_LOGIN_CREDENTIALS_MESSAGE, serializer.errors)
        # serializer.save()
        self._edit_user(user, request.data)
        return self._get_user(pk)
