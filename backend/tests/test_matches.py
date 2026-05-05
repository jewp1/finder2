from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.matches.models import Match
from apps.likes.models import Like

User = get_user_model()


def make_user(email='u@example.com', username='user', password='pass1234'):
    return User.objects.create_user(email=email, username=username, password=password)


class MatchListTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_a = make_user('a@example.com', 'userA')
        self.user_b = make_user('b@example.com', 'userB')
        self.user_c = make_user('c@example.com', 'userC')
        Match.objects.create(user=self.user_a, liked_user=self.user_b, status=Match.STATUS_ACCEPTED)
        Match.objects.create(user=self.user_a, liked_user=self.user_c, status=Match.STATUS_PENDING)

    def test_returns_own_matches(self):
        self.client.force_authenticate(user=self.user_a)
        res = self.client.get('/api/v1/matches/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.json()), 2)

    def test_does_not_return_others_matches(self):
        self.client.force_authenticate(user=self.user_b)
        res = self.client.get('/api/v1/matches/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.json()), 0)

    def test_match_item_has_user(self):
        self.client.force_authenticate(user=self.user_a)
        res = self.client.get('/api/v1/matches/')
        items_with_user = [item for item in res.json() if 'user' in item]
        self.assertEqual(len(items_with_user), 2)

    def test_deduplication_same_user(self):
        Match.objects.create(user=self.user_a, liked_user=self.user_b, status=Match.STATUS_PENDING)
        self.client.force_authenticate(user=self.user_a)
        res = self.client.get('/api/v1/matches/')
        user_ids = [item['user']['id'] for item in res.json() if 'user' in item]
        self.assertEqual(len(user_ids), len(set(user_ids)))

    def test_unauthenticated(self):
        res = self.client.get('/api/v1/matches/')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PotentialMatchesTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_a = make_user('a@example.com', 'userA')
        self.user_b = make_user('b@example.com', 'userB')
        self.user_c = make_user('c@example.com', 'userC')
        self.user_d = make_user('d@example.com', 'userD')

    def test_excludes_self(self):
        self.client.force_authenticate(user=self.user_a)
        res = self.client.get('/api/v1/matches/potential')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ids = [u['id'] for u in res.json()]
        self.assertNotIn(self.user_a.id, ids)

    def test_excludes_already_matched(self):
        Match.objects.create(user=self.user_a, liked_user=self.user_b, status=Match.STATUS_PENDING)
        self.client.force_authenticate(user=self.user_a)
        res = self.client.get('/api/v1/matches/potential')
        ids = [u['id'] for u in res.json()]
        self.assertNotIn(self.user_b.id, ids)

    def test_excludes_already_liked(self):
        Like.objects.create(user=self.user_a, liked_user=self.user_c)
        self.client.force_authenticate(user=self.user_a)
        res = self.client.get('/api/v1/matches/potential')
        ids = [u['id'] for u in res.json()]
        self.assertNotIn(self.user_c.id, ids)

    def test_includes_unreached_users(self):
        self.client.force_authenticate(user=self.user_a)
        res = self.client.get('/api/v1/matches/potential')
        ids = [u['id'] for u in res.json()]
        self.assertIn(self.user_b.id, ids)
        self.assertIn(self.user_c.id, ids)
        self.assertIn(self.user_d.id, ids)

    def test_unauthenticated(self):
        res = self.client.get('/api/v1/matches/potential')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class CreateMatchTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_a = make_user('a@example.com', 'userA')
        self.user_b = make_user('b@example.com', 'userB')

    def url(self, user_id):
        return f'/api/v1/matches/{user_id}'

    def test_create_match_success(self):
        self.client.force_authenticate(user=self.user_a)
        res = self.client.post(self.url(self.user_b.id))
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        body = res.json()
        self.assertEqual(body['status'], Match.STATUS_PENDING)
        self.assertIn('user', body)
        self.assertEqual(body['user']['id'], self.user_b.id)

    def test_create_match_persisted(self):
        self.client.force_authenticate(user=self.user_a)
        self.client.post(self.url(self.user_b.id))
        self.assertTrue(Match.objects.filter(user=self.user_a, liked_user=self.user_b).exists())

    def test_create_match_not_found(self):
        self.client.force_authenticate(user=self.user_a)
        res = self.client.post(self.url(9999))
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_match_unauthenticated(self):
        res = self.client.post(self.url(self.user_b.id))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_match_sets_mutual_likes_when_reverse_exists(self):
        reverse_like = Like.objects.create(user=self.user_b, liked_user=self.user_a)
        own_like = Like.objects.create(user=self.user_a, liked_user=self.user_b)

        self.client.force_authenticate(user=self.user_a)
        self.client.post(self.url(self.user_b.id))

        own_like.refresh_from_db()
        reverse_like.refresh_from_db()
        self.assertTrue(own_like.is_mutual)
        self.assertTrue(reverse_like.is_mutual)

    def test_create_match_no_mutual_without_reverse_like(self):
        self.client.force_authenticate(user=self.user_a)
        self.client.post(self.url(self.user_b.id))
        self.assertFalse(Like.objects.filter(user=self.user_a, liked_user=self.user_b, is_mutual=True).exists())


class UpdateMatchStatusTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_a = make_user('a@example.com', 'userA')
        self.user_b = make_user('b@example.com', 'userB')
        self.match = Match.objects.create(
            user=self.user_a,
            liked_user=self.user_b,
            status=Match.STATUS_PENDING,
        )

    def url(self, match_id=None):
        return f'/api/v1/matches/{match_id or self.match.id}/status'

    def test_update_to_accepted(self):
        self.client.force_authenticate(user=self.user_a)
        res = self.client.put(self.url(), {'status': 'accepted'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.json()['status'], 'accepted')
        self.match.refresh_from_db()
        self.assertEqual(self.match.status, Match.STATUS_ACCEPTED)

    def test_update_to_rejected(self):
        self.client.force_authenticate(user=self.user_a)
        res = self.client.put(self.url(), {'status': 'rejected'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.json()['status'], 'rejected')

    def test_update_to_pending(self):
        self.match.status = Match.STATUS_ACCEPTED
        self.match.save()
        self.client.force_authenticate(user=self.user_a)
        res = self.client.put(self.url(), {'status': 'pending'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_update_invalid_status(self):
        self.client.force_authenticate(user=self.user_a)
        res = self.client.put(self.url(), {'status': 'invalid_status'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', res.json())

    def test_update_not_found(self):
        self.client.force_authenticate(user=self.user_a)
        res = self.client.put(self.url(9999), {'status': 'accepted'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_wrong_owner_is_404(self):
        self.client.force_authenticate(user=self.user_b)
        res = self.client.put(self.url(), {'status': 'accepted'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_unauthenticated(self):
        res = self.client.put(self.url(), {'status': 'accepted'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
