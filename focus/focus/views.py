import json
from typing import Text, Any, Dict, Optional
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.renderers import JSONRenderer
from rest_framework import status


def _get_error_response(code: int, message: Text, data: Any, **kwargs) -> Response:
    return Response({
        "error_code": code, "error_message": message, "data": data
    }, status=kwargs.get("status", status.HTTP_400_BAD_REQUEST))


def page_not_found_view(request, exception):
    response = _get_error_response(
        0, "Hi", {})
    response.accepted_renderer = JSONRenderer()
    response.accepted_media_type = "application/json"
    response.renderer_context = {}
    return response
