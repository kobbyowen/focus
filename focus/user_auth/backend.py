from typing import Optional, Tuple, Text
import jwt
from django.conf import settings
from rest_framework import authentication, exceptions
from rest_framework.request import Request
from .models import User


class JWTAuthentication(authentication.BaseAuthentication):
    authentication_header_prefix = 'Bearer'

    def authenticate(self, request: Request) -> Optional[Tuple[User, Text]]:
        request.user = None

        header = authentication.get_authorization_header(
            request).decode().split()

        if not header or len(header) != 2:
            return None

        prefix, token = header
        if prefix.lower() != self.authentication_header_prefix.lower():
            return None

        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms='HS256')
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed("Token has expired")
        except jwt.exceptions.InvalidTokenError:
            import traceback
            traceback.print_exc()
            raise exceptions.AuthenticationFailed("Invalid token")

        try:
            user = User.objects.get(id=payload['id'])
        except User.DoesNotExist:
            msg = 'Invalid token. User cannot be found'
            raise exceptions.AuthenticationFailed(msg)

        return (user, token)
