import json
import re
import unicodedata
from pathlib import Path
from collections import Counter

#common words
Stop_words = {
    "the", "is", "am", "are", "a", "an", "and", "or",
    "to", "of", "in", "on", "it", "this", "that",
    "i", "you", "he", "she", "we", "they", "me",
    "my", "your", "what", "how", "do", "does"
    }

def count_emojis(text):
    count = 0
    for char in text:
        code = ord(char)
        if (0x1F300 <= code <= 0x1FAFF or 0x2600 <= code <= 0x27BF):
            count += 1
    return count

#analyzing participant messages
def analyze_participant(messages):
    total_messages = len(messages)

    if total_messages == 0:
        return {}

    all_text = ' '.join(msg["message"] for msg in messages)

    words = re.findall(
        r"[a-zA-Z]+(?:'[a-zA-Z]+)?", all_text.lower()
    )

    useful_words = [word for word in words if word not in Stop_words and len(word) > 1]

    word_frequency = Counter(useful_words)

    total_words = len(words)

    average_words = total_words / total_messages

    average_characters = (
        sum(len(msg["message"]) for msg in messages) / total_messages
    )

    question_count = sum(
        "?" in msg["message"] for msg in messages
    )

    exclamation_count = sum(
        "!" in msg["message"] for msg in messages
    )

    emoji_count = sum(
        count_emojis(msg["message"]) for msg in messages
    )

    uppercase_count = sum(
        sum(char.isupper() for char in msg["message"]) for msg in messages
    ) 

    alphabet_count = sum(
        sum(char.isalpha() for char in msg["message"]) for msg in messages
    )

    uppercase_ratio = (
        uppercase_count / alphabet_count if alphabet_count else 0
    )

    profile = {
        "total_messages":total_messages,
        "total_words":total_words,
        "average_words_per_message":round(average_words, 2),
        "average_characters_per_message":round(average_characters,2),
        "question_messages":question_count,
        "exclamation_messages":exclamation_count,
        "uppercase_letter_ratio":uppercase_ratio,
        "total_emojis":emoji_count,
        "top_words":word_frequency.most_common(10)
    }
    return profile

#analyzing chat
def analyze_chat(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        messages = json.load(file)

    participants = {}

    #grouping messages by sender
    for message in messages:
        sender = message["sender"]
        if sender not in participants:
                participants[sender] = []
        participants[sender].append(message)

    #analyze every participant
    profiles = {}
    for sender, sender_message in participants.items():
        profiles[sender] = analyze_participant(
            sender_message
        )
    return profiles

if __name__ == "__main__":
    input_file = Path("../data/parsed_chat.json")
    output_file = Path("../data/personality_profiles.json")
    profiles = analyze_chat(input_file)
    print("\nChatPersona - Style analysis")
    print("="*40)
    for sender, profile in profiles.items():
        print("\n Partifipant: ",sender)
        for key, value in profile.items():
            print(f"{key}:{value}")

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(
            profiles,
            file,
            indent=4,
            ensure_ascii=False
        )
    print("Profile saved successfully.")