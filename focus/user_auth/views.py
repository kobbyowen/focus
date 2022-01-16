from typing import Text, Dict, Any
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import AllowAny
from .serializers import RegistrationSerializer, LoginSerializer
from rest_framework.response import Response
from rest_framework.request import Request
from focus.errors import *


def _get_error_response(code: int, message: Text, data: Any, **kwargs) -> Response:
    return Response({
        "error_code": code, "error_message": message, "data": data
    }, status=kwargs.get("status", status.HTTP_400_BAD_REQUEST))


def _get_success_response(data: Any, **kwargs: Dict[Text, Any]) -> Response:

    return Response({
        "error_code": SUCCESS_CODE, "error_message": SUCCESS_MESSAGE, "data": data
    }, status=kwargs.get("status", status.HTTP_200_OK))


class RegistrationAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = RegistrationSerializer

    def post(self, request: Request) -> Response:
        data = request.data
        serializer = self.serializer_class(data=data)
        if not serializer.is_valid():
            return _get_error_response(MISSING_PARAMETER_CODE, MISSING_PARAMETER_MESSAGE, serializer.errors)
        serializer.save()
        return _get_success_response({}, status=status.HTTP_201_CREATED)


class LoginAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request: Request) -> Response:
        data = request.data
        serializer = self.serializer_class(data=data)
        if not serializer.is_valid():
            return _get_error_response(INVALID_LOGIN_CREDENTIALS_CODE, INVALID_LOGIN_CREDENTIALS_MESSAGE, serializer.errors)
        return _get_success_response(serializer.data)
