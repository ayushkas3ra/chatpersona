import re
import json
from pathlib import Path

def parse_chat(file_path):
    messages = []
    pattern = re.compile(
        r"^\[(.*?)\]\s(.*?):\s(.*)$"
    )
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            match = pattern.match(line)
            if match:
                timestamp, sender, message = match.groups()
                messages.append({
                    "timestamp":timestamp,
                    "sender":sender,
                    "message":message
                    })
            elif messages:
                #Handle messages spanning multiple lines
                messages[-1]["message"] += "\n" + line
    return messages

if __name__ == "__main__":
    file_path = Path("../data/sample_chats/sample.txt")
    chat_data = parse_chat(file_path)
    print("\nCHAT PERSONA - PARSER OUTPUT")
    print("-" * 40)
    for msg in chat_data:
        print(msg)
    print("\nTotal messages:", len(chat_data))
    with open("../data/parsed_chat.json", "w", encoding="utf-8") as file:
        json.dump(chat_data, file, indent=4, ensure_ascii=False)

    print("\nParsed data saved successfully!")