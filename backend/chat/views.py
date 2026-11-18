from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import ChatRequestSerializer

from response_generator import load_profiles, generate_response
from memory import initialize_database, load_history
from vector_memory import sync_memories
from memory import get_user_messages

@api_view(["POST"])
def chat_message(request):
    serializer = ChatRequestSerializer(data=request.data)

    serializer.is_valid(raise_exception=True)

    participant = serializer.validated_data["participant"]
    message = serializer.validated_data["message"]

    profiles = load_profiles()

    if participant not in profiles:
        return Response(
            {
                "error": "Participant not found!",
                status: status.HTTP_400_BAD_REQUEST
            }
        )

    initialize_database()

    history = load_history(participant)

    #keep semantic memory synchronised
    stored_messages = get_user_messages(participant)
    sync_memories(stored_messages, participant)

    reply = generate_response(
        sender = participant,
        user_message = message,
        profiles = profiles,
        history=history
    )

    return Response(
        {
            "participant": participant,
            "reply": reply
        }
    )