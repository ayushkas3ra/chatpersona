from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import ChatRequestSerializer

from response_generator import load_profiles, generate_response
from memory import initialize_database, load_history
from vector_memory import sync_memories
from memory import get_user_messages

import logging

logger = logging.getLogger(__name__)

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

    try:
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
    except Exception:
        logger.exception("Chat response generation failed!")
        return Response(
            {
                "message": "Unable to generate response, please try again.",
                status: status.HTTP_503_SERVICE_UNAVAILABLE
            }
        )

    return Response(
        {
            "participant": participant,
            "reply": reply
        }
    )

@api_view(["GET"])
def chat_history(request):
    participant = request.query_params.get("participant")

    if not participant:
        return Response(
            {"message": "Participant required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    profiles = load_profiles()

    if participant not in profiles:
        return Response(
            {"message": "Participant not found!"},
            status=status.HTTP_404_NOT_FOUND
        )

    history = load_history(participant)

    messages = [
        {
            "id": index,
            "role": message["role"],
            "content": message["content"]
        }
        for index, message in enumerate(history)
    ]

    return Response({
        "participant": participant,
        "messages": messages
    })