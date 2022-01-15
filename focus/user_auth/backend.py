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

        header = authentication.get_authorization_header(request).split()

        if not header or len(header) != 2:
            return None

        prefix, token = map(str.decode, header)

        if prefix.lower() != self.authentication_header_prefix:
            return None

        return self._authenticate(request, token)

        try:
            payload = jwt.decode(token, settings.SECRET_KEY)
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed("Token has expired")
        except jwt.exceptions.InvalidTokenError:
            raise exceptions.AuthenticationFailed("Invalid token")

        try:
            user = User.objects.get(pk=payload['id'])
        except User.DoesNotExist:
            msg = 'Invalid token. User cannot be found'
            raise exceptions.AuthenticationFailed(msg)

        return (user, token)
