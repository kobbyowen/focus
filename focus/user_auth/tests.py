from django.test import TestCase, Client


class TestListUsersView(TestCase):
    def setUp(self):
        self.client = Client()

    def test_list_users(self):
        pass

    def test_list_user_unauthorized(self):
        pass


class TestUserView(TestCase):
    def setUp(self):
        self.client = Client()

    def test_add_user(self):
        pass
