from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()

URL_REGISTER = "/api/v1/auth/register"
URL_LOGIN = "/api/v1/auth/login"
URL_ME = "/api/v1/auth/me"
URL_USERS = "/api/v1/users/"


class RegisterTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "password123",
            "full_name": "Test User",
        }

    def test_register_success(self):
        res = self.client.post(URL_REGISTER, self.data, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        body = res.json()
        self.assertIn("access_token", body)
        self.assertEqual(body["token_type"], "bearer")
        self.assertEqual(body["user"]["email"], "test@example.com")
        self.assertEqual(body["user"]["username"], "testuser")

    def test_register_creates_user_in_db(self):
        self.client.post(URL_REGISTER, self.data, format="json")
        self.assertTrue(User.objects.filter(email="test@example.com").exists())

    def test_register_password_is_hashed(self):
        self.client.post(URL_REGISTER, self.data, format="json")
        user = User.objects.get(email="test@example.com")
        self.assertNotEqual(user.password, "password123")
        self.assertTrue(user.check_password("password123"))

    def test_register_without_optional_fields(self):
        data = {"email": "min@example.com", "username": "minuser", "password": "pass123"}
        res = self.client.post(URL_REGISTER, data, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_register_duplicate_email(self):
        User.objects.create_user(email="test@example.com", username="other", password="pass123")
        res = self.client.post(URL_REGISTER, self.data, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_username(self):
        User.objects.create_user(email="other@example.com", username="testuser", password="pass123")
        res = self.client.post(URL_REGISTER, self.data, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_password_too_short(self):
        res = self.client.post(URL_REGISTER, {**self.data, "password": "12345"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", res.json())

    def test_register_username_too_short(self):
        res = self.client.post(URL_REGISTER, {**self.data, "username": "ab"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_full_name_too_short(self):
        res = self.client.post(URL_REGISTER, {**self.data, "full_name": "A"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_invalid_email(self):
        res = self.client.post(URL_REGISTER, {**self.data, "email": "not-an-email"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_missing_email(self):
        data = {k: v for k, v in self.data.items() if k != "email"}
        res = self.client.post(URL_REGISTER, data, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_missing_username(self):
        data = {k: v for k, v in self.data.items() if k != "username"}
        res = self.client.post(URL_REGISTER, data, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_missing_password(self):
        data = {k: v for k, v in self.data.items() if k != "password"}
        res = self.client.post(URL_REGISTER, data, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_response_does_not_contain_password(self):
        res = self.client.post(URL_REGISTER, self.data, format="json")
        self.assertNotIn("password", res.json().get("user", {}))


class LoginTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="user@example.com",
            username="loginuser",
            password="securepass",
        )

    def test_login_by_email(self):
        res = self.client.post(URL_LOGIN, {"username": "user@example.com", "password": "securepass"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        body = res.json()
        self.assertIn("access_token", body)
        self.assertEqual(body["token_type"], "bearer")
        self.assertIn("user", body)

    def test_login_by_username(self):
        res = self.client.post(URL_LOGIN, {"username": "loginuser", "password": "securepass"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", res.json())

    def test_login_wrong_password(self):
        res = self.client.post(URL_LOGIN, {"username": "user@example.com", "password": "wrongpass"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", res.json())

    def test_login_nonexistent_user(self):
        res = self.client.post(URL_LOGIN, {"username": "nobody@example.com", "password": "anypass"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_inactive_user(self):
        self.user.is_active = False
        self.user.save()
        res = self.client.post(URL_LOGIN, {"username": "user@example.com", "password": "securepass"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", res.json())

    def test_login_missing_password(self):
        res = self.client.post(URL_LOGIN, {"username": "user@example.com"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_missing_username(self):
        res = self.client.post(URL_LOGIN, {"password": "securepass"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_empty_body(self):
        res = self.client.post(URL_LOGIN, {}, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class MeTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="me@example.com",
            username="meuser",
            password="pass123",
            full_name="Me User",
        )

    def test_me_returns_current_user(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.get(URL_ME)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        body = res.json()
        self.assertIn("user", body)
        self.assertEqual(body["user"]["email"], "me@example.com")
        self.assertEqual(body["user"]["username"], "meuser")

    def test_me_unauthenticated(self):
        res = self.client.get(URL_ME)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_does_not_expose_password(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.get(URL_ME)
        self.assertNotIn("password", res.json()["user"])


class UserListTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email="a@example.com", username="usera", password="pass")
        User.objects.create_user(email="b@example.com", username="userb", password="pass")

    def test_list_authenticated(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.get(URL_USERS)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.json()), 2)

    def test_list_unauthenticated(self):
        res = self.client.get(URL_USERS)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
