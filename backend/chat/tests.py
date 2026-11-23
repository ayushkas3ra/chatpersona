from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from chat.models import ChatImport, Persona, ChatMessage

from unittest.mock import patch

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

    def test_history_rejects_non_existent_persona(self):
        response = self.client.get("/api/history/?persona_id=9999999")

        self.assertEqual(response.status_code, 404)

        self.assertIn("detail", response.data)

    def test_history_rejects_invalid_persona_id(self):
        response = self.client.get("/api/history/", {"persona_id": 0})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"], "Invalid persona id")

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

    def test_upload_generates_personality_profiles(self):
        file = SimpleUploadedFile(
            "friends.txt",
            (
                b"[22/11/2026, 08:00] Rahul: Hello!\n"
                b"[22/11/2026, 08:01] Ayush: Hi!\n"
                b"[22/11/2026, 08:03] Rahul: How are you?"
            ),
            content_type="text/plain",
        )

        response = self.client.post("/api/uploads/", {"file": file}, format="multipart")

        self.assertEqual(response.status_code, 201)

        Rahul = Persona.objects.get(
            chat_import_id=response.data["id"], participant_name="Rahul"
        )

        Ayush = Persona.objects.get(
            chat_import_id=response.data["id"], participant_name="Ayush"
        )

        self.assertEqual(Rahul.personality_data["total_messages"], 2)

        self.assertEqual(Ayush.personality_data["total_messages"], 1)

        self.assertIn("average_words_per_message", Rahul.personality_data)

    def test_user_can_not_access_other_users_persona(self):
        other_user = User.objects.create_user(
            username="otheruser", password="StrongTestPassword123!"
        )

        other_import = ChatImport.objects.create(
            user=other_user, original_filename="private.txt"
        )

        other_persona = Persona.objects.create(
            chat_import=other_import, participant_name=other_user
        )

        response = self.client.post(
            "/api/chat/",
            {"persona_id": other_persona.id, "message": "Hello"},
            format="json",
        )

        self.assertEqual(response.status_code, 404)

    @patch("chat.views.generate_persona_response")
    def test_chat_saves_messages_for_correct_persona(self, mock_generate):
        mock_generate.return_value = "Hey there!"

        # create chat_import
        chat_import = ChatImport.objects.create(
            user=self.user, original_filename="freinds.txt"
        )

        # create persona
        persona = Persona.objects.create(
            chat_import=chat_import,
            participant_name="Rahul",
            personality_data={"total_messages": 10},
        )

        # response.post
        response = self.client.post(
            "/api/chat/", {"persona_id": persona.id, "message": "Hello!"}, format="json"
        )

        # self.assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["reply"], "Hey there!")

        # filter messages by persona
        messages = ChatMessage.objects.filter(persona=persona).order_by("id")

        # assert equal
        self.assertEqual(messages.count(), 2)

        self.assertEqual(messages[0].role, "user")
        self.assertEqual(messages[0].content, "Hello!")

        self.assertEqual(messages[1].role, "assistant")
        self.assertEqual(messages[1].content, "Hey there!")

        # mock_generate
        mock_generate.assert_called_once()

    def user_can_not_read_another_user_chat_history(self):
        other_user = User.objects.create_user(
            username="otheruser", password="StrongTestPassword123!"
        )

        other_import = ChatImport.objects.create(
            user=other_user, original_filename="private.txt"
        )

        other_persona = Persona.objects.create(
            chat_import=other_import, participant_name="Rahul"
        )

        ChatMessage.objects.create(
            persona=other_persona, role="user", content="Private message"
        )

        response = self.client.get(reverse("history"), {"persona_id": other_persona.id})

        self.assertEqual(response.status_code, 404)
