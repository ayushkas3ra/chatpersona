import sqlite3
from pathlib import Path

import re
from collections import Counter

#Database location
BASE_DIR = Path(__file__).resolve().parent.parent
DB_FILE = BASE_DIR / "data" / "chatpersona.db"

#Connect to database
def get_connection():
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_FILE)

    return connection

#create database table
def initialize_database():
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        participant TEXT NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    connection.commit()
    connection.close()

#save a message
def save_message(participant, role, content):
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute('''
        INSERT INTO messages (participant, role, content)
        VALUES (?, ?, ?)
    ''', (participant, role, content))

    message_id = cursor.lastrowid # id of latest inserted message

    connection.commit()
    connection.close()

    return message_id

#load recent conversation history
def load_history(participant, limit = 20):
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute('''
        SELECT role, content FROM messages WHERE participant = ? ORDER BY id DESC Limit ?
    ''',(participant, limit))

    rows = cursor.fetchall()

    connection.close()

    #reverse to set order from latest to oldest
    rows.reverse()

    history = []

    for role, content in rows:
        history.append(
            {
                "role": role,
                "content": content
            }
        )

    return history

#Display stored messages
def show_history(participant):
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute('''
        SELECT role, content, created_at FROM messages WHERE participant = ? ORDER BY id ASC 
    ''', (participant,))

    rows = cursor.fetchall()

    connection.close()

    for role, content, created_at in rows:
        print(f"\n[{created_at}] {role}: {content}")

#search older messages using keyword matching
def search_history(participant, query, limit = 5):
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute('SELECT role, content FROM messages WHERE participant = ? ORDER BY id ASC', (participant,))

    rows = cursor.fetchall()

    connection.close()

    #Extract words from user's question
    query_words = set(re.findall(r"[a-zA-Z]+", query.lower()))

    #removing stop_words
    stop_words = {
        "what", "is", "am", "are", "the", "a", "an",
        "i", "you", "he", "she", "we", "they",
        "did", "do", "does", "my", "your", "me",
        "in", "on", "at", "to", "of", "and",
        "it", "which", "who", "when", "where",
        "how", "was", "were", "have", "has"
    }

    query_words = query_words - stop_words

    scored_messages = []

    for role, content in rows:
        #Extract words froms stored messages
        message_words = set(re.findall(r"[a-zA-Z]+", content.lower()))

        #count matching keywords
        common_words = query_words.intersection(message_words)

        score = len(common_words)

        if score > 0:
            scored_messages.append({
                "role":role,
                "content":content,
                "score": score
            })

    #sort by relevence
    scored_messages.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    #return the most relevent messages
    results = []

    for item in scored_messages[:limit]:
        results.append({
            "role":item["role"],
            "content":item["content"]
        })

    return results

#fetching raw text from sqlite by message id which is a primary key in db
def get_message_by_id(message_id):
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute('SELECT content FROM messages WHERE id = ?', (message_id,))

    row = cursor.fetchone()

    connection.close()

    if row is None:
        return None

    return row[0]

#get user messages and skip ai messages
def get_user_messages(participant):
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("SELECT id, content FROM messages WHERE participant = ? AND role = 'user'", (participant,))

    messages = cursor.fetchall()

    return messages

#Test database independently
if __name__ == "__main__":
    initialize_database()

    print("\nChatPersona database initialized!")

    print("\nDB location:", DB_FILE)
