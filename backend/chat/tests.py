from django.test import TestCase
from rest_framework.test import APIClient


class ChatAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()

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