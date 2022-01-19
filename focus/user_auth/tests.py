import json
from typing import Dict, Text, Any, Optional
from django.test import TestCase, Client
from django.http import HttpResponse
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


class TestRegistrationAPIView(TestCase):
    def setUp(self):
        self.client = Client()
        self.super_user, self.super_auth_headers, self.user, self.auth_header = _pre_test()

    def tearDown(self):
        self.super_user.delete()
        self.user.delete()

    def test_registration_with_existing_email(self):
        response, code = _send_request(self.client, "/auth/register", "POST", {
                                       "email": "kobbyowen@gmail.com", "username": "ko", "name": "Kobby", "password": "Password@1"})
        self.assertNotEqual(response["error_code"], 0)
        self.assertNotEqual(code, 200)

    def test_registration_with_existing_username(self):
        response, code = _send_request(self.client, "/auth/register", "POST", {
                                       "email": "kobbyowen000@gmail.com", "username": "kobbyowen", "name": "Kobby", "password": "Password@1"})
        self.assertNotEqual(response["error_code"], 0)
        self.assertNotEqual(code, 200)

    def test_registration_with_valid_inputs(self):
        response, code = _send_request(self.client, "/auth/register", "POST", {
                                       "email": "kobbyowen0000@gmail.com", "username": "kobbyowen00", "name": "Kobby", "password": "Password@1"})
        self.assertEqual(response["error_code"], 0)
        self.assertEqual(code, 201)

    def test_registration_with_missing_parameters(self):
        body = {"email": "kobbyowen000@gmail.com", "username": "kobbyowen",
                "name": "Kobby", "password": "Password@1"}
        keys = list(body.keys())
        for key in keys:
            b_copy = body.copy()
            b_copy.pop(key)
            response, code = _send_request(
                self.client, "/auth/register", "POST", b_copy)
            self.assertNotEqual(response["error_code"], 0)
            self.assertNotEqual(code, 200)


class TestLoginAPIView(TestCase):
    def setUp(self):
        self.client = Client()
        self.super_user, self.super_auth_headers, self.user, self.auth_header = _pre_test()

    def tearDown(self):
        self.super_user.delete()
        self.user.delete()

    def test_login_with_invalid_credentials(self):
        response, code = _send_request(self.client, "/auth/login", "POST", {
                                       "email": "kobbyow000n@gmail.com",  "password": "password@1"})
        self.assertNotEqual(response["error_code"], 0)
        self.assertNotEqual(code, 200)

    def test_login_with_valid_credentials(self):
        response, code = _send_request(
            self.client, "/auth/login", "POST", {"email": "kobbyowen@gmail.com",  "password": "password@1"})
        self.assertEqual(response["error_code"], 0)
        self.assertEqual(code, 200)
        self.assertIn("token", response["data"])

    def test_login_with_missing_parameters(self):
        body = {"email": "kobbyowen000@gmail.com", "password": "password@1"}
        keys = list(body.keys())
        for key in keys:
            b_copy = body.copy()
            b_copy.pop(key)
            response, code = _send_request(
                self.client, "/auth/login", "POST", b_copy)
            self.assertNotEqual(response["error_code"], 0)
            self.assertNotEqual(code, 200)
