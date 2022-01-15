from unittest import TestCase
from unittest.mock import patch
from focus.auth.models import UserManager


class TestUserManager(TestCase):

    def test_create_user_with_blank_email(self):
        user = UserManager()

    def test_create_user_with_blank_username(self):
        pass

    def test_create_user_with_blank_name(self):
        pass

    def test_create_user(self):
        pass

    def test_create_admin(self):
        pass
