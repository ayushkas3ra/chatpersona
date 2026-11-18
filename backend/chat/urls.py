from django.urls import path
from .views import chat_message

urlpatterns = [
    path("chat/", chat_message, name="chat-message")
]