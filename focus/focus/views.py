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


def page_not_found_view(request, exception):
    response = _get_error_response(
        RESOURCE_NOT_FOUND_CODE, RESOURCE_NOT_FOUND_MESSAGE, None, status=status.HTTP_404_NOT_FOUND)
    response.accepted_renderer = JSONRenderer()
    response.accepted_media_type = "application/json"
    response.renderer_context = {}
    return response
