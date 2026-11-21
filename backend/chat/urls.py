from django.urls import path
from .views import chat_message, chat_history, list_personas, upload_chat

urlpatterns = [
    path("chat/", chat_message, name="chat-message"),
    path("history/", chat_history, name="chat-history"),
    path("personas/", list_personas, name="list-personas"),
    path("uploads/", upload_chat, name="upload-chat")
]