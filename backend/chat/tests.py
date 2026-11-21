from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

class ChatAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

        User = get_user_model()

        self.user = User.objects.create_user(
            username="testuser",
            password="TestPassword123"
        )

        self.client.force_authenticate(user=self.user)

    def test_chat_requires_message(self):
        response = self.client.post(
            "/api/chat/",
            {"participant": "Rahul", "message": ""},
            format="json"
        )

        self.assertEqual(response.status_code, 400)

    def test_chat_requires_participant(self):
        response = self.client.post(
            "/api/chat/",
            {"message": "Hello"},
            format="json"
        )

        self.assertEqual(response.status_code, 400)

    def test_history_requires_participant(self):
        response = self.client.get("/api/history/")

        self.assertEqual(response.status_code, 400)

    def test_history_rejects_empty_participant(self):
        response = self.client.get(
            "/api/history/?participant="
        )

        self.assertEqual(response.status_code, 400)

    def test_history_rejects_non_existent_participant(self):
        response = self.client.get(
            "/api/history/?participant=UnknownPerson"
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.data["message"],
            "Participant not found!"
        )

    def test_unauthenticated_user_can_not_access_chat_history(self):
        self.client.force_authenticate(user = None)

        response = self.client.get(
            '/api/history/'
        )

        self.assertEqual(response.status_code, 403)