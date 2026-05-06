from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.likes.models import Like
from apps.matches.models import Match
from apps.projects.models import Project

User = get_user_model()


def make_user(email="u@example.com", username="user", password="pass1234"):
    return User.objects.create_user(email=email, username=username, password=password)


class LikeUserTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_a = make_user("a@example.com", "userA")
        self.user_b = make_user("b@example.com", "userB")

    def url(self, user_id):
        return f"/api/v1/likes/user/{user_id}"

    def test_like_user_success(self):
        self.client.force_authenticate(user=self.user_a)
        res = self.client.post(self.url(self.user_b.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("message", res.json())
        self.assertTrue(Like.objects.filter(user=self.user_a, liked_user=self.user_b).exists())

    def test_like_yourself_rejected(self):
        self.client.force_authenticate(user=self.user_a)
        res = self.client.post(self.url(self.user_a.id))
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", res.json())

    def test_like_nonexistent_user(self):
        self.client.force_authenticate(user=self.user_a)
        res = self.client.post(self.url(9999))
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_like_idempotent(self):
        self.client.force_authenticate(user=self.user_a)
        self.client.post(self.url(self.user_b.id))
        res = self.client.post(self.url(self.user_b.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(Like.objects.filter(user=self.user_a, liked_user=self.user_b).count(), 1)

    def test_like_unauthenticated(self):
        res = self.client.post(self.url(self.user_b.id))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_mutual_like_sets_is_mutual(self):
        self.client.force_authenticate(user=self.user_a)
        self.client.post(self.url(self.user_b.id))

        self.client.force_authenticate(user=self.user_b)
        self.client.post(self.url(self.user_a.id))

        like_a = Like.objects.get(user=self.user_a, liked_user=self.user_b)
        like_b = Like.objects.get(user=self.user_b, liked_user=self.user_a)
        self.assertTrue(like_a.is_mutual)
        self.assertTrue(like_b.is_mutual)

    def test_mutual_like_creates_accepted_matches(self):
        self.client.force_authenticate(user=self.user_a)
        self.client.post(self.url(self.user_b.id))
        self.client.force_authenticate(user=self.user_b)
        self.client.post(self.url(self.user_a.id))

        self.assertTrue(
            Match.objects.filter(user=self.user_a, liked_user=self.user_b, status=Match.STATUS_ACCEPTED).exists()
        )
        self.assertTrue(
            Match.objects.filter(user=self.user_b, liked_user=self.user_a, status=Match.STATUS_ACCEPTED).exists()
        )

    def test_one_sided_like_not_mutual(self):
        self.client.force_authenticate(user=self.user_a)
        self.client.post(self.url(self.user_b.id))

        like = Like.objects.get(user=self.user_a, liked_user=self.user_b)
        self.assertFalse(like.is_mutual)

    def test_one_sided_like_no_match_created(self):
        self.client.force_authenticate(user=self.user_a)
        self.client.post(self.url(self.user_b.id))

        self.assertFalse(Match.objects.filter(user=self.user_a, liked_user=self.user_b).exists())


class UserLikesListTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_a = make_user("a@example.com", "userA")
        self.user_b = make_user("b@example.com", "userB")
        self.user_c = make_user("c@example.com", "userC")
        Like.objects.create(user=self.user_a, liked_user=self.user_b)
        Like.objects.create(user=self.user_a, liked_user=self.user_c)

    def test_returns_liked_users(self):
        self.client.force_authenticate(user=self.user_a)
        res = self.client.get("/api/v1/likes/user/likes")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.json()
        self.assertEqual(len(data), 2)
        liked_ids = {item["user"]["id"] for item in data}
        self.assertIn(self.user_b.id, liked_ids)
        self.assertIn(self.user_c.id, liked_ids)

    def test_empty_when_no_likes(self):
        self.client.force_authenticate(user=self.user_b)
        res = self.client.get("/api/v1/likes/user/likes")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.json(), [])

    def test_does_not_include_project_likes(self):
        owner = make_user("owner@example.com", "owneruser")
        project = Project.objects.create(title="P", description="D", owner=owner)
        Like.objects.create(user=self.user_a, project=project)
        self.client.force_authenticate(user=self.user_a)
        res = self.client.get("/api/v1/likes/user/likes")
        self.assertEqual(len(res.json()), 2)

    def test_unauthenticated(self):
        res = self.client.get("/api/v1/likes/user/likes")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class UserLikedByTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_a = make_user("a@example.com", "userA")
        self.user_b = make_user("b@example.com", "userB")
        Like.objects.create(user=self.user_b, liked_user=self.user_a)

    def test_returns_users_who_liked_me(self):
        self.client.force_authenticate(user=self.user_a)
        res = self.client.get("/api/v1/likes/user/liked-by")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["user"]["id"], self.user_b.id)

    def test_empty_when_nobody_liked(self):
        self.client.force_authenticate(user=self.user_b)
        res = self.client.get("/api/v1/likes/user/liked-by")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.json(), [])

    def test_unauthenticated(self):
        res = self.client.get("/api/v1/likes/user/liked-by")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class LikeProjectTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = make_user()
        self.owner = make_user("owner@example.com", "owneruser")
        self.project = Project.objects.create(title="Test", description="Test", owner=self.owner)

    def url(self, project_id):
        return f"/api/v1/likes/project/{project_id}"

    def test_like_project_success(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.post(self.url(self.project.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("like_id", res.json())
        self.assertTrue(Like.objects.filter(user=self.user, project=self.project).exists())

    def test_like_project_idempotent(self):
        self.client.force_authenticate(user=self.user)
        self.client.post(self.url(self.project.id))
        res = self.client.post(self.url(self.project.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(Like.objects.filter(user=self.user, project=self.project).count(), 1)

    def test_like_project_not_found(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.post(self.url(9999))
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_like_project_unauthenticated(self):
        res = self.client.post(self.url(self.project.id))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class LikeMatchesTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_a = make_user("a@example.com", "userA")
        self.user_b = make_user("b@example.com", "userB")
        self.user_c = make_user("c@example.com", "userC")
        Like.objects.create(user=self.user_a, liked_user=self.user_b, is_mutual=True)
        Like.objects.create(user=self.user_a, liked_user=self.user_c, is_mutual=False)

    def test_returns_only_mutual_likes(self):
        self.client.force_authenticate(user=self.user_a)
        res = self.client.get("/api/v1/likes/matches")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["user"]["id"], self.user_b.id)
        self.assertTrue(data[0]["is_mutual"])

    def test_empty_when_no_mutual_likes(self):
        self.client.force_authenticate(user=self.user_c)
        res = self.client.get("/api/v1/likes/matches")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.json(), [])

    def test_unauthenticated(self):
        res = self.client.get("/api/v1/likes/matches")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
