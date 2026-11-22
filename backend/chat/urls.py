from django.urls import path
from .views import chat_history, list_personas, upload_chat, chat_view

urlpatterns = [
    path("chat/", chat_view, name="chat"),
    path("history/", chat_history, name="chat-history"),
    path("personas/", list_personas, name="list-personas"),
    path("uploads/", upload_chat, name="upload-chat")
]