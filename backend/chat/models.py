from django.db import models
from django.conf import settings


class ChatImport(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="chat_imports"
    )

    original_filename = models.CharField(max_length=255)

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.original_filename} - {self.user}"


class Persona(models.Model):
    chat_import = models.ForeignKey(
        ChatImport, on_delete=models.CASCADE, related_name="personas"
    )

    participant_name = models.CharField(max_length=100)

    personality_data = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["chat_import", "participant_name"],
                name="unique_participant_per_import",
            )
        ]

    def __str__(self):
        return self.participant_name


class ChatMessage(models.Model):
    ROLE_CHOICES = [("user", "User"), ("assistant", "Assistant")]

    persona = models.ForeignKey(
        Persona, on_delete=models.CASCADE, related_name="messages"
    )

    role = models.CharField(max_length=10)

    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.persona.participant_name}-{self.role}"
