from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from chat.models import ChatImport, Persona

User = get_user_model()


class ChatAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

        User = get_user_model()

        self.user = User.objects.create_user(
            username="testuser", password="TestPassword123"
        )

        self.client.force_authenticate(user=self.user)

    def test_chat_requires_message(self):
        response = self.client.post(
            "/api/chat/", {"participant": "Rahul", "message": ""}, format="json"
        )

        self.assertEqual(response.status_code, 400)

    def test_chat_requires_participant(self):
        response = self.client.post("/api/chat/", {"message": "Hello"}, format="json")

        self.assertEqual(response.status_code, 400)

    def test_history_requires_participant(self):
        response = self.client.get("/api/history/")

        self.assertEqual(response.status_code, 400)

    def test_history_rejects_empty_participant(self):
        response = self.client.get("/api/history/?participant=")

        self.assertEqual(response.status_code, 400)

    def test_history_rejects_non_existent_participant(self):
        response = self.client.get("/api/history/?participant=UnknownPerson")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data["message"], "Participant not found!")

    def test_unauthenticated_user_can_not_access_chat_history(self):
        self.client.force_authenticate(user=None)

        response = self.client.get("/api/history/")

        self.assertEqual(response.status_code, 403)

    def test_user_can_only_see_own_personas(self):
        other_user = User.objects.create_user(
            username="otheruser", password="StrongTestPassword123!"
        )

        my_import = ChatImport.objects.create(
            user=self.user, original_filename="my_chat.txt"
        )

        other_import = ChatImport.objects.create(
            user=other_user, original_filename="other_chat.txt"
        )

        my_persona = Persona.objects.create(
            chat_import=my_import, participant_name="Rahul"
        )

        Persona.objects.create(chat_import=other_import, participant_name="Rahul")

        response = self.client.get("/api/personas/")

        self.assertEqual(response.status_code, 200)

        personas = response.data["personas"]

        self.assertEqual(len(personas), 1)
        self.assertEqual(personas[0]["id"], my_persona.id)

    def test_authenticated_user_can_upload_chat(self):
        file = SimpleUploadedFile(
            "friends.txt",
            (
                b"[20/11/2026, 10:30] Rahul: Hello!\n"
                b"[20/11/2026, 10:31] Ayush: Hey!\n"
                b"[20/11/2026, 10:32] Rahul: How are you?"
            ),
            content_type="text/plain",
        )

        response = self.client.post("/api/uploads/", {"file": file}, format="multipart")

        print("API RESPONSE:", response.data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["message_count"], 3)

        chat_import = ChatImport.objects.get(id=response.data["id"])

        self.assertEqual(chat_import.user, self.user)

        personas = Persona.objects.filter(chat_import=chat_import)

        self.assertEqual(personas.count(), 2)

        self.assertEqual(
            set(personas.values_list("participant_name", flat=True)), {"Rahul", "Ayush"}
        )

    def test_upload_rejects_invalid_utf8(self):
        file = SimpleUploadedFile(
            "invalid.txt", b"\xff\xfe\xfa", content_type="text/plain"
        )

        response = self.client.post("/api/uploads/", {"file": file}, format="multipart")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(ChatImport.objects.count(), 0)
