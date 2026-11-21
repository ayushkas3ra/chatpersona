from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser

from .serializers import ChatRequestSerializer, ChatUploadSerializer

from response_generator import load_profiles, generate_response
from memory import initialize_database, load_history
from vector_memory import sync_memories
from memory import get_user_messages

from .models import Persona, ChatImport
from pathlib import Path

import logging

from django.db import transaction

from chat_parser import parse_chat_text

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
            {"error": "Participant not found!", status: status.HTTP_400_BAD_REQUEST}
        )

    initialize_database()

    try:
        history = load_history(participant)

        # keep semantic memory synchronised
        stored_messages = get_user_messages(participant)
        sync_memories(stored_messages, participant)

        reply = generate_response(
            sender=participant, user_message=message, profiles=profiles, history=history
        )
    except Exception:
        logger.exception("Chat response generation failed!")
        return Response(
            {
                "message": "Unable to generate response, please try again.",
                status: status.HTTP_503_SERVICE_UNAVAILABLE,
            }
        )

    return Response({"participant": participant, "reply": reply})


@api_view(["GET"])
def chat_history(request):
    participant = request.query_params.get("participant")

    if not participant:
        return Response(
            {"message": "Participant required"}, status=status.HTTP_400_BAD_REQUEST
        )

    profiles = load_profiles()

    if participant not in profiles:
        return Response(
            {"message": "Participant not found!"}, status=status.HTTP_404_NOT_FOUND
        )

    history = load_history(participant)

    messages = [
        {"id": index, "role": message["role"], "content": message["content"]}
        for index, message in enumerate(history)
    ]

    return Response({"participant": participant, "messages": messages})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_personas(request):
    personas = Persona.objects.filter(chat_import__user=request.user).order_by(
        "-created_at"
    )

    data = [
        {
            "id": persona.id,
            "participant_name": persona.participant_name,
            "chat_import_id": persona.chat_import_id,
        }
        for persona in personas
    ]

    return Response({"personas": data})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser])
def upload_chat(request):
    serializer = ChatUploadSerializer(data=request.data)

    serializer.is_valid(raise_exception=True)

    uploaded_file = serializer.validated_data["file"]

    uploaded_file.seek(0)

    content = uploaded_file.read().decode(("utf-8-sig"))

    print("RAW CONTENT:", repr(content))
    print("LINES:", content.splitlines())

    messages = parse_chat_text(content)

    if not messages:
        return Response(
            {"error": "No valid whatsapp messages found!"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    participants = sorted({message["sender"] for message in messages})

    with transaction.atomic():
        chat_import = ChatImport.objects.create(
            user=request.user, original_filename=Path(uploaded_file.name).name
        )

    personas = [
        Persona.objects.create(chat_import=chat_import, participant_name=participant)
        for participant in participants
    ]

    return Response(
        {
            "id": chat_import.id,
            "filename": chat_import.original_filename,
            "message_count": len(messages),
            "personas": [
                {"id": persona.id, "participant_name": persona.participant_name}
                for persona in personas
            ],
        },
        status=status.HTTP_201_CREATED,
    )
