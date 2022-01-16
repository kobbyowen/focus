from typing import Optional, Text, Dict, Any
from datetime import timedelta, datetime
import jwt
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core import validators
from django.conf import settings


class UserManager(BaseUserManager):

    def _create_user(self,  email: Text, username: Text, name: Text, password: Optional[Text] = None, **kwargs: Dict[Text, Any]) -> AbstractBaseUser:
        args = (email, username, name)
        if not all(args):
            arg = list(filter(args, lambda x: x == ''))[0]
            raise ValueError(f'{arg!r} is required')

        user: AbstractBaseUser = self.model(
            email=self.normalize_email(email),
            username=username,
            name=name
        )

        user.set_password(password)
        user.is_admin = kwargs.get("admin", False)

        user.save(using=self._db)

        return user

    def create_user(self,  email: Text, username: Text, name: Text, password: Optional[Text] = None) -> AbstractBaseUser:
        return self._create_user(email, username, name, password)

    def create_superuser(self,  email: Text, username: Text, name: Text, password: Optional[Text] = None) -> AbstractBaseUser:
        return self._create_user(email, username, name, password, admin=True)


class User(PermissionsMixin, AbstractBaseUser):
    name = models.CharField(max_length=512)
    username = models.CharField(max_length=128, unique=True)
    email = models.EmailField(unique=True, max_length=512, validators=[
                              validators.validate_email])
    is_admin = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ("name", "username")

    objects = UserManager()

    def __str__(self) -> Text:
        return f"<User : {self.username}>"

    @property
    def is_staff(self) -> Text:
        return self.is_admin

    @property
    def token(self) -> Text:
        return self._generate_token()

    def _generate_token(self) -> Text:
        expiry_date = datetime.now() + timedelta(seconds=settings.TOKEN_LIEFTIME)

        token = jwt.encode({
            'id': self.pk,
            'exp': int(expiry_date.strftime('%s'))
        }, settings.SECRET_KEY, algorithm='HS256')

        return token
