import json
from pathlib import Path
from ollama import chat

import os
from dotenv import load_dotenv

load_dotenv()

from memory import initialize_database, save_message, load_history, get_user_messages

from vector_memory import search_semantic_memory, sync_memories, save_embedding

# project paths
BASE_DIR = Path(__file__).resolve().parent.parent

PROFILE_FILE = BASE_DIR / "data" / "personality_profiles.json"

MODEL_NAME = os.getenv("OLLAMA_MODEL")

MAX_HISTORY = 20


# load participant profiles
def load_profiles():
    with open(PROFILE_FILE, "r", encoding="utf-8") as file:
        profiles = json.load(file)
        return profiles


# generate a communication-style-based response
def generate_response(sender, user_message, profiles, history):
    if sender not in profiles:
        raise ValueError(f"Participant {sender} not found.")

    if not user_message.strip():
        raise ValueError("messages can not be empty.")

    profile = profiles[sender]

    # search sqlite for relevent messages
    # relevent_history = search_history(sender,user_message, limit=5)
    relevent_history = search_semantic_memory(
        question=user_message, participant=sender, n_results=3
    )
    print(f"\nRetrieved {len(relevent_history)} relevent memories!")

    # convert profile into readable information
    style_information = json.dumps(profile, indent=2, ensure_ascii=False)

    # convert retrieved memories into readable text
    memory_information = json.dumps(relevent_history, indent=2, ensure_ascii=False)

    # instructions for qwen

    system_prompt = f"""
    You are ChatPersona, an AI conversational style simulator.

    Your task is to generate fictional responses using the
    communication style described below.

    COMMUNICATION PROFILE:
    {style_information}

    RELEVANT OLDER CONVERSATION MEMORIES:

    {memory_information}

    Use these retrieved messages as additional context.
    They may contain information from much older conversations.
    Prioritize actual conversation evidence over guesses.

    IMPORTANT CONVERSATION RULES:

    1. Carefully read the entire conversation history.
    2. Previous user messages contain important information.
    3. When the user asks what they previously said,
    retrieve the answer from conversation history.
    4. Never ignore information explicitly mentioned earlier.
    5. Do not invent memories or facts.
    6. If information is not present in the history,
    honestly say you don't know.
    7. Use the participant's observed vocabulary and
    messaging style.
    8. Keep responses natural and conversational.
    9. Use emojis and punctuation appropriately.
    10. Never claim to actually be the participant.

    Return only the suggested reply.
    """

    # prepare messages for qwen
    messages = [{"role": "system", "content": system_prompt}]

    # add previous conversation
    messages.extend(history)

    # add curent message
    messages.append({"role": "user", "content": user_message})

    # send the request to qwen
    # response = chat(
    #     model=MODEL_NAME,
    #     messages=[
    #         {
    #             "role":"system",
    #             "content":system_prompt
    #         },
    #         {
    #             "role":"user",
    #             "content":user_message
    #         }
    #     ],
    #     options = {
    #         "temperature":0.2
    #     }
    # )
    response = chat(model=MODEL_NAME, messages=messages, options={"temperature": 0.2})
    reply = response.message.content

    # save user message in sqlite
    message_id = save_message(sender, "user", user_message)

    # saving embedding of new message in sqlite
    try:
        save_embedding(message_id, user_message, sender)
        print("New memory embedding saved!")
    except Exception as error:
        print(f"Embedding failed: {error}")

    # save AI message in sqlite
    save_message(sender, "assistant", reply)

    # saving conversation history
    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": reply})

    # keeping only last 20 messages
    if len(history) > MAX_HISTORY:
        history[:] = history[-MAX_HISTORY:]

    return reply


# new response generator
def generate_persona_response(user_message, personality_profile, history, persona_id):
    # check is message is empty
    if not user_message.strip():
        raise ValueError("Message can not be empty!")

        # retrieve relevent older memories
    try:
        relevent_memories = search_semantic_memory(
            question=user_message, persona_id=persona_id, n_results=3
        )
    except Exception:
        relevent_memories = []

    # dump style information
    style_information = json.dumps(personality_profile, indent=2, ensure_ascii=False)

    memory_information = json.dumps(relevent_memories, indent=2, ensure_ascii=False)

    # system prompt
    system_prompt = f"""
    You are ChatPersona, an AI communication-style simulator.

    Generate a fictional response using the communication
    style described below.

    COMMUNICATION PROFILE:
    {style_information}

    RELEVENT_PREVIOUS_MEMORIES:
    {memory_information}

    RULES:
    1. Use the vocabulary and writing style in the profile.
    2. Keep responses natural and conversational.
    3. Use emojis and punctuation appropriately.
    4. Consider previous conversation messages.
    5. Never invent memories or personal facts.
    6. Never claim to actually be the participant.
    7. If you don't know something, say so.

    Return only the suggested reply.
    """

    # message
    messages = [{"role": "system", "content": system_prompt}]

    # extend message
    messages.extend(history)

    # append user message in message
    messages.append({"role": "user", "content": user_message})

    # generate response
    response = chat(model=MODEL_NAME, messages=messages, options={"temperature": 0.2})

    # return respose content
    return response.message.content


# main program
if __name__ == "__main__":
    # initialize sqlite
    initialize_database()

    print("\nDatabase connnected successfully")

    profiles = load_profiles()

    # separate memory for each participant
    # converation_memory = {
    #     sender : [] for sender in profiles
    # }

    print("\nChatPersona AI response generator")
    print("=" * 45)

    # display available participants
    print("\n Available participants: ")

    for sender in profiles:
        print("-", sender)

    selected_sender = input("Select a participant: ").strip()

    if selected_sender not in profiles:
        print("Participant not found!")
        raise SystemExit(1)

    # sync sqlite with chroma
    stored_messages = get_user_messages(selected_sender)
    sync_memories(stored_messages, selected_sender)

    print("\nAI simulation selected:", selected_sender)
    print("\nMemory enabled!")
    print("Type 'exit' to stop.")

    # history = converation_memory[selected_sender]
    # load previous conversation with sqlite
    history = load_history(selected_sender)
    print(f"\nLoaded {len(history)} previous messages")

    while True:
        user_message = input("\nYou: ").strip()

        if user_message.lower() == "exit":
            print("ChatPersona closed.")
            break

        if not user_message:
            print("Please enter a message!")
            continue

        try:
            reply = generate_response(selected_sender, user_message, profiles, history)

            print("\nChatPersona:", reply)

            print(f"\n[Memory: {len(history)} message stored]")

        except Exception as error:
            print("\nSomething went wrong", error)
