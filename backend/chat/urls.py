from django.urls import path
from .views import chat_message, chat_history

urlpatterns = [
    path("chat/", chat_message, name="chat-message"),
    path("history/", chat_history, name="chat-history")
]