from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser

from .serializers import (
    ChatRequestSerializer,
    ChatUploadSerializer,
    SendMessageSerializer,
)

from response_generator import (
    load_profiles,
    generate_response,
    generate_persona_response,
)
from memory import initialize_database, load_history, get_user_messages
from vector_memory import sync_memories

from .models import Persona, ChatImport, ChatMessage
from pathlib import Path

import logging

from django.db import transaction
from django.shortcuts import get_object_or_404

from chat_parser import parse_chat_text
from personality_analyzer import analyze_participant

from collections import defaultdict

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
            {"error": "Participant not found!"}, status=status.HTTP_400_BAD_REQUEST
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
            {"error": "Unable to generate response, please try again."},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    return Response({"participant": participant, "reply": reply})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def chat_history(request):
    # get persona id from request
    persona_id = request.query_params.get("persona_id")

    # if not persona id then error
    if not persona_id:
        return Response(
            {"error": "Persona id is required"}, status=status.HTTP_400_BAD_REQUEST
        )

    # check persona id is valid
    try:
        persona_id = int(persona_id)
        if persona_id <= 0:
            raise ValueError
    except (ValueError, TypeError):
        return Response(
            {"error": "Invalid persona id"}, status=status.HTTP_400_BAD_REQUEST
        )

    # get persona by Persona persona_id and user
    persona = get_object_or_404(Persona, id = persona_id, chat_import__user=request.user)

    # filter messages in ChatMessage
    messages = ChatMessage.objects.filter(persona=persona).order_by("id")

    # extract data(id, role, content) from messages
    data = [
        {"id": message.id, "role": message.role, "content": message.content}
        for message in messages
    ]

    # return persona_id, participant_name and messages
    return Response(
        {
            "persona_id": persona.id,
            "participant_name": persona.participant_name,
            "messages": data,
        }
    )


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

    messages = parse_chat_text(content)

    if not messages:
        return Response(
            {"error": "No valid whatsapp messages found!"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # retrieveing messages by each sender i.e.
    # {"Rahul":[{"sender": "Rahul", "message": "Hey"}, {"sender": "Rahul", "message": "Hello"}],
    # "Ayush":[{"sender":"Ayush", "message":"How are you?"}, {"sender":"Ayush", "message": "I am fine."}]}
    messages_by_sender = defaultdict(list)  # initializing default dictionary

    for message in messages:
        messages_by_sender[message["sender"]].append(message)

    with transaction.atomic():
        chat_import = ChatImport.objects.create(
            user=request.user, original_filename=Path(uploaded_file.name).name
        )

        Personas = []

        for participant, participant_messages in sorted(messages_by_sender.items()):
            profile = analyze_participant(participant_messages)
            persona = Persona.objects.create(
                chat_import=chat_import,
                participant_name=participant,
                personality_data=profile,
            )
            Personas.append(persona)

    return Response(
        {
            "id": chat_import.id,
            "filename": chat_import.original_filename,
            "message_count": len(messages),
            "personas": [
                {"id": persona.id, "participant_name": persona.participant_name}
                for persona in Personas
            ],
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def chat_view(request):
    serializer = SendMessageSerializer(data=request.data)

    serializer.is_valid(raise_exception=True)

    persona_id = serializer.validated_data["persona_id"]
    user_message = serializer.validated_data["message"]

    # checking ownership of persona to the current user
    persona = get_object_or_404(Persona, id=persona_id, chat_import__user=request.user)

    persona_profile = persona.personality_data

    # loading history of this persona profile
    previous_messages = ChatMessage.objects.filter(persona=persona).order_by(
        "-created_at", "-id"
    )[:20]

    history = [
        {"role": message.role, "content": message.content}
        for message in reversed(previous_messages)
    ]

    # generate AI response
    try:
        reply = generate_persona_response(
            user_message=user_message,
            personality_profile=persona_profile,
            history=history,
        )
    except Exception:
        logger.exception("Failed to generate AI response")
        return Response(
            {"error": "Unable to generate response"},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    # save conversation to django db
    with transaction.atomic():
        ChatMessage.objects.create(persona=persona, role="user", content=user_message)
        ChatMessage.objects.create(persona=persona, role="assistant", content=reply)

    # return response
    return Response({"persona_id": persona.id, "reply": reply})
