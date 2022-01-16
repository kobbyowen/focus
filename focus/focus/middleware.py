import json
from typing import Text, Any, Dict, Optional
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.renderers import JSONRenderer
from rest_framework import status
from .errors import *


def _get_error_response(code: int, message: Text, data: Any, **kwargs) -> Response:
    return Response({
        "error_code": code, "error_message": message, "data": data
    }, status=kwargs.get("status", status.HTTP_400_BAD_REQUEST))


class HandleExceptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: Request):
        response = self.get_response(request)
        return response

    def process_exception(self, request: Request, exception: Exception) -> Optional[Response]:
        import traceback
        traceback.print_exc()
        response = _get_error_response(
            GENERAL_ERROR_CODE, GENERAL_ERROR_MESSAGE, {})
        response.accepted_renderer = JSONRenderer()
        response.accepted_media_type = "application/json"
        response.renderer_context = {}
        return response

    def unauthorized_response(self, request: Request, exception: Exception) -> Optional[Response]:
        response = _get_error_response(
            UNAUTHORIZED_ACCESS_CODE, UNAUTHORIZED_ACCESS_MESSAGE, {})

        response.accepted_renderer = JSONRenderer()
        response.accepted_media_type = "application/json"
        response.renderer_context = {}

        return response
