from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.projects.models import Project

User = get_user_model()

URL_PROJECTS = "/api/v1/projects/"


def make_user(email="u@example.com", username="user", password="pass1234"):
    return User.objects.create_user(email=email, username=username, password=password)


def make_project(owner, title="Test Project", description="A test project"):
    return Project.objects.create(title=title, description=description, owner=owner)


class ProjectListTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.owner = make_user()
        make_project(self.owner, title="Alpha Project", description="About algorithms")
        make_project(self.owner, title="Beta System", description="Backend service")

    def test_list_public_access(self):
        res = self.client.get(URL_PROJECTS)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.json()), 2)

    def test_list_includes_owner(self):
        res = self.client.get(URL_PROJECTS)
        project = res.json()[0]
        self.assertIn("owner", project)
        self.assertIn("email", project["owner"])

    def test_list_search_by_title(self):
        res = self.client.get(URL_PROJECTS, {"search": "Alpha"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        results = res.json()
        self.assertEqual(len(results), 1)
        self.assertIn("Alpha", results[0]["title"])

    def test_list_search_by_description(self):
        res = self.client.get(URL_PROJECTS, {"search": "algorithms"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.json()), 1)

    def test_list_search_case_insensitive(self):
        res = self.client.get(URL_PROJECTS, {"search": "alpha"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.json()), 1)

    def test_list_search_no_results(self):
        res = self.client.get(URL_PROJECTS, {"search": "XYZ_NONEXISTENT"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.json(), [])

    def test_list_pagination_limit(self):
        res = self.client.get(URL_PROJECTS, {"limit": 1})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.json()), 1)

    def test_list_pagination_skip(self):
        res_all = self.client.get(URL_PROJECTS)
        res_skip = self.client.get(URL_PROJECTS, {"skip": 1})
        self.assertEqual(len(res_skip.json()), len(res_all.json()) - 1)

    def test_list_ordered_by_newest_first(self):
        from datetime import timedelta

        from django.utils import timezone

        Project.objects.filter(title="Alpha Project").update(created_at=timezone.now() - timedelta(seconds=10))
        res = self.client.get(URL_PROJECTS)
        items = res.json()
        self.assertEqual(items[0]["title"], "Beta System")


class ProjectCreateTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = make_user()
        self.data = {
            "title": "New Project",
            "description": "A brand new project",
            "status": "open",
        }

    def test_create_authenticated(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.post(URL_PROJECTS, self.data, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        body = res.json()
        self.assertEqual(body["title"], "New Project")
        self.assertEqual(body["owner_id"], self.user.id)

    def test_create_unauthenticated(self):
        res = self.client.post(URL_PROJECTS, self.data, format="json")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_missing_title(self):
        self.client.force_authenticate(user=self.user)
        data = {k: v for k, v in self.data.items() if k != "title"}
        res = self.client.post(URL_PROJECTS, data, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_missing_description(self):
        self.client.force_authenticate(user=self.user)
        data = {k: v for k, v in self.data.items() if k != "description"}
        res = self.client.post(URL_PROJECTS, data, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_requirements_as_list(self):
        self.client.force_authenticate(user=self.user)
        data = {**self.data, "requirements": ["Python", "Django", "Docker"]}
        res = self.client.post(URL_PROJECTS, data, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.json()["requirements"], ["Python", "Django", "Docker"])

    def test_create_requirements_as_comma_string(self):
        self.client.force_authenticate(user=self.user)
        data = {**self.data, "requirements": "Python, Django"}
        res = self.client.post(URL_PROJECTS, data, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        reqs = res.json()["requirements"]
        self.assertIsInstance(reqs, list)
        self.assertIn("Python", reqs)
        self.assertIn("Django", reqs)

    def test_create_default_status_is_open(self):
        self.client.force_authenticate(user=self.user)
        data = {"title": "No Status", "description": "Test"}
        res = self.client.post(URL_PROJECTS, data, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.json()["status"], "open")

    def test_create_with_optional_fields(self):
        self.client.force_authenticate(user=self.user)
        data = {**self.data, "budget": "$5000", "duration": "3 months"}
        res = self.client.post(URL_PROJECTS, data, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.json()["budget"], "$5000")
        self.assertEqual(res.json()["duration"], "3 months")


class ProjectDetailTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.owner = make_user()
        self.project = make_project(self.owner)

    def test_get_detail_public(self):
        res = self.client.get(f"/api/v1/projects/{self.project.pk}")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.json()["id"], self.project.id)

    def test_get_detail_includes_owner(self):
        res = self.client.get(f"/api/v1/projects/{self.project.pk}")
        self.assertIn("owner", res.json())

    def test_get_detail_not_found(self):
        res = self.client.get("/api/v1/projects/9999")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)


class ProjectUpdateTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.owner = make_user()
        self.other = make_user(email="other@example.com", username="otheruser")
        self.project = make_project(self.owner)

    def url(self):
        return f"/api/v1/projects/{self.project.pk}"

    def test_update_by_owner(self):
        self.client.force_authenticate(user=self.owner)
        res = self.client.put(self.url(), {"title": "Updated", "description": "New desc"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.json()["title"], "Updated")

    def test_update_partial(self):
        self.client.force_authenticate(user=self.owner)
        res = self.client.put(self.url(), {"title": "Only Title"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.json()["title"], "Only Title")

    def test_update_by_non_owner(self):
        self.client.force_authenticate(user=self.other)
        res = self.client.put(self.url(), {"title": "Hacked"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_unauthenticated(self):
        res = self.client.put(self.url(), {"title": "No Auth"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_not_found(self):
        self.client.force_authenticate(user=self.owner)
        res = self.client.put("/api/v1/projects/9999", {"title": "X"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_status(self):
        self.client.force_authenticate(user=self.owner)
        res = self.client.put(self.url(), {"status": "in_progress"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.json()["status"], "in_progress")


class ProjectDeleteTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.owner = make_user()
        self.other = make_user(email="other@example.com", username="otheruser")
        self.project = make_project(self.owner)

    def url(self):
        return f"/api/v1/projects/{self.project.pk}"

    def test_delete_by_owner(self):
        self.client.force_authenticate(user=self.owner)
        res = self.client.delete(self.url())
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertFalse(Project.objects.filter(pk=self.project.pk).exists())

    def test_delete_response_message(self):
        self.client.force_authenticate(user=self.owner)
        res = self.client.delete(self.url())
        self.assertIn("message", res.json())

    def test_delete_by_non_owner(self):
        self.client.force_authenticate(user=self.other)
        res = self.client.delete(self.url())
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Project.objects.filter(pk=self.project.pk).exists())

    def test_delete_unauthenticated(self):
        res = self.client.delete(self.url())
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_not_found(self):
        self.client.force_authenticate(user=self.owner)
        res = self.client.delete("/api/v1/projects/9999")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
