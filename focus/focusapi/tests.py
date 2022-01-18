import json
from typing import Dict, Text, Any, Optional
from django.test import TestCase, Client
from unittest.mock import patch
from django.http import HttpResponse
from django.db.models.signals import post_save, pre_save
from focus.signals import catch_user_changes_response
from focusapi.models import User
from focus.errors import *


def _send_request(client: Client,  url: Text, method: Optional[Text] = "GET", request_body: Optional[Dict[Text, Any]] = None, headers: Optional[Dict[Text, Text]] = None, **kwargs) -> HttpResponse:
    headers = headers or {}
    client_call = client.get
    if method == "POST":
        client_call = client.post
    elif method == "PUT":
        client_call = client.put
    elif method == "DELETE":
        client_call = client.delete
    response = client_call(url, request_body, **
                           headers) if request_body else client_call(url, **headers)
    code = response.status_code
    response = response.content.decode()
    try:
        response = json.loads(response)
    except json.JSONDecodeError:
        pass
    finally:
        return response, code


def _pre_test():
    super_user = User.objects.create_superuser(
        "kobbyowen@gmail.com", "kobbyowen", "Kobby Owen", "password@1")
    user = User.objects.create_user(
        "kobbyowen0@gmail.com", "kobbyowen0", "kobbyowen", "password@1")
    super_user_token = super_user.token
    user_token = user.token
    super_auth_headers = {
        "HTTP_AUTHORIZATION": f"Bearer {super_user_token}"}
    auth_headers = {
        "HTTP_AUTHORIZATION": f"Bearer {user_token}"}

    return super_user, super_auth_headers, user, auth_headers


class TestListUsersView(TestCase):
    def setUp(self):
        self.client = Client()
        self.super_user, self.super_auth_headers, self.user, self.auth_headers = _pre_test()

    def tearDown(self):
        self.super_user.delete()
        self.user.delete()

    def test_list_users_by_normal_user(self):
        # normal users cannot list all users
        response, code = _send_request(
            self.client, "/api/v1/users",  headers=self.auth_headers)
        self.assertNotEqual(response["error_code"], 0)
        self.assertEqual(code, 403)

    def test_list_users_by_super_user(self):
        response, code = _send_request(
            self.client,  "/api/v1/users",  headers=self.super_auth_headers)
        self.assertEqual(response["error_code"], 0)
        self.assertEqual(code, 200)

    def test_list_user_unauthorized(self):
        response, code = _send_request(
            self.client,  "/api/v1/users")
        self.assertNotEqual(response["error_code"], 0)
        self.assertEqual(code, 403)


class TestUserView(TestCase):
    def setUp(self):
        self.client = Client()
        self.super_user, self.super_auth_headers, self.user, self.auth_headers = _pre_test()

    def test_get_user_by_superuser(self):
        response, code = _send_request(
            self.client, f"/api/v1/user/{self.user.id}", headers=self.super_auth_headers)
        self.assertEqual(response["error_code"], SUCCESS_CODE)

    def test_get_other_user_by_normal_user(self):
        response, code = _send_request(
            self.client, f"/api/v1/user/{self.super_user.id}", headers=self.auth_headers)
        self.assertEqual(response["error_code"], FORBIDDEN_CODE)
        self.assertEqual(code, 403)

    def test_get_same_user_by_normal_user(self):
        response, code = _send_request(
            self.client, f"/api/v1/user/{self.user.id}", headers=self.auth_headers)
        self.assertEqual(response["error_code"], SUCCESS_CODE)

    def test_edit_signal_sent(self):
        with patch('focus.signals.catch_user_changes_response', autospec=True) as mocked_handler:
            pre_save.connect(mocked_handler, sender=User,
                             dispatch_uid='test_mock')

            response, code = _send_request(
                self.client, f"/api/v1/user/{self.user.id}", request_body={"username": "owen333"}, headers=self.auth_headers)
            self.assertEqual(response["error_code"], SUCCESS_CODE)
            mocked_handler.assert_called()

    def test_edit_username(self):
        response, code = _send_request(
            self.client, f"/api/v1/user/{self.user.id}", request_body={"username": "owen333"}, headers=self.auth_headers)
        self.assertEqual(response["error_code"], SUCCESS_CODE)
        self.assertTrue(User.objects.get(pk=self.user.id).username, "owen333")

    def test_edit_another_users_account(self):
        response, code = _send_request(
            self.client, f"/api/v1/user/{self.super_user.id}", request_body={"username": "owen333"}, headers=self.auth_headers)
        self.assertNotEqual(response["error_code"], SUCCESS_CODE)

    def test_edit_user_email(self):
        response, code = _send_request(
            self.client, f"/api/v1/user/{self.user.id}", request_body={"email": "k.owen000000@nsano.com"}, headers=self.auth_headers)
        self.assertEqual(response["error_code"], SUCCESS_CODE)
        self.assertTrue(User.objects.get(pk=self.user.id).email,
                        "k.owen000000@nsano.com")

    def test_edit_user_name(self):
        response, code = _send_request(
            self.client, f"/api/v1/user/{self.user.id}", request_body={"name": "kobby owen"}, headers=self.auth_headers)
        self.assertEqual(response["error_code"], SUCCESS_CODE)
        self.assertTrue(User.objects.get(pk=self.user.id).name,
                        "kobby owen")
