from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient


class HealthViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_health_returns_200(self):
        res = self.client.get("/health")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_health_response_has_required_keys(self):
        res = self.client.get("/health")
        body = res.json()
        self.assertIn("status", body)
        self.assertIn("database", body)
        self.assertIn("api", body)

    def test_health_database_is_connected(self):
        res = self.client.get("/health")
        body = res.json()
        self.assertEqual(body["database"], "connected")
        self.assertEqual(body["status"], "healthy")

    def test_health_api_is_running(self):
        res = self.client.get("/health")
        self.assertEqual(res.json()["api"], "running")

    def test_health_no_auth_required(self):
        res = self.client.get("/health")
        self.assertNotEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class RootViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_root_returns_200(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_root_response_has_message_and_version(self):
        res = self.client.get("/")
        body = res.json()
        self.assertIn("message", body)
        self.assertIn("version", body)

    def test_root_welcome_message_content(self):
        res = self.client.get("/")
        self.assertIn("Project Finder", res.json()["message"])

    def test_root_no_auth_required(self):
        res = self.client.get("/")
        self.assertNotEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
