import json
from pathlib import Path
from ollama import chat

#project paths
BASE_DIR = Path(__file__).resolve().parent.parent

PROFILE_FILE = BASE_DIR / "data" / "personality_profiles.json"

MODEL_NAME = "qwen3:1.7b"

MAX_HISTORY = 20

#load participant profiles
def load_profiles():
    with open(PROFILE_FILE, "r", encoding="utf-8") as file:
        profiles = json.load(file)
        return profiles

#generate a communication-style-based response
def generate_response(sender, user_message, profiles, history):
    if sender not in profiles:
        raise ValueError(f"Participant {sender} not found.")
    
    if not user_message.strip():
        raise ValueError("messages can not be empty.")

    profile = profiles[sender]

    #convert profile into readable information
    style_information = json.dumps(
        profile,
        indent=2,
        ensure_ascii=False
    )

    #instructions for qwen
    
    system_prompt = f"""
    You are ChatPersona, an AI conversational style simulator.

    Your task is to generate fictional responses using the
    communication style described below.

    COMMUNICATION PROFILE:
    {style_information}

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

    #prepare messages for qwen
    messages = [
        {
            "role":"system",
            "content":system_prompt
        }
    ]

    #add previous conversation
    messages.extend(history)

    #add curent message
    messages.append(
        {
            "role":"user",
            "content": user_message
        }
    )

    #send the request to qwen
    response = chat(
        model=MODEL_NAME,
        messages=[
            {
                "role":"system",
                "content":system_prompt
            },
            {
                "role":"user",
                "content":user_message
            }
        ],
        options = {
            "temperature":0.2
        }
    )
    reply =  response.message.content

    #saving conversation history
    history.append({
        "role":"user",
        "content":user_message
    })
    history.append({
        "role":"assistant",
        "content":reply
    })

    #keeping only last 20 messages
    if len(history) > MAX_HISTORY:
        history[:] = history[-MAX_HISTORY:]

    return reply

#main program
if __name__ == '__main__':
    profiles = load_profiles()

    #separate memory for each participant
    converation_memory = {
        sender : [] for sender in profiles
    }

    print('\nChatPersona AI response generator')
    print("="*45)

    #display available participants
    print("\n Available participants: ")

    for sender in profiles:
        print("-",sender)

    selected_sender = input("Select a participant: ").strip()

    if selected_sender not in profiles:
        print("Participant not found!")
        raise SystemExit(1)

    print("\nAI simulation selected:", selected_sender)
    print("\nMemory enabled!")
    print("Type 'exit' to stop.")

    history = converation_memory[selected_sender]

    while True:
        user_message = input("\nYou: ").strip()

        if user_message.lower() == "exit":
            print("ChatPersona closed.")
            break

        if not user_message:
            print("Please enter a message!")
            continue

        try:
            reply = generate_response(
                selected_sender,
                user_message,
                profiles,
                history
            )

            print("\nChatPersona:",reply)

            print(f"\n[Memory: {len(history)} message stored]")

        except Exception as error:
            print("\nSomething went wrong", error)
