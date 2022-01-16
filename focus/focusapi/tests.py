from django.test import TestCase, Client


class TestListUsersView(TestCase):
    def setUp(self):
        self.client = Client()
        response = self.client.post(
            "auth/login", {"email": "k.owen000000@nsano.com", "password": "Jesus@33"})
        print(response.content)

    def test_list_users(self):
        pass

    def test_list_user_unauthorized(self):
        pass


class TestUserView(TestCase):
    def setUp(self):
        self.client = Client()

    def test_add_user(self):
        pass
