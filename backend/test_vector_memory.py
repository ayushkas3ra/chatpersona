# from vector_memory import save_embedding, collection, get_embedding
# from memory import get_message_by_id

# save_embedding(1, "I love to code in python language.")

# print("Embedding saved successfully.")

# result = collection.get(
#     ids=['1'],
#     include=["embeddings"]
# )
# print(result)

# question = "In which language I code?"

# question_embedding = get_embedding(question, "nomic-embed-text")

# results = collection.query(
#     query_embeddings=[question_embedding],
#     n_results=3
# )

# print(results["ids"])

# message_ids = ['15', '8', '23']

# messages = []

# for message_id in message_ids:
#     message = get_message_by_id(message_id)

#     if message is not None:
#         messages.append(message)

# print(messages)

# from vector_memory import search_semantic_memory, get_similar_embeddings_ids, Chroma_PATH, collection
# from memory import get_message_by_id

# print("Chroma path:", Chroma_PATH)
# print("Stored embeddings:", collection.count())

# question = "What programming language do I like?"

# ids = get_similar_embeddings_ids(question)

# print("ChromaDB:", ids)

# messages = search_semantic_memory(question)

# print("Relevent messages: ")
# for message_id in ids:
#     message = get_message_by_id(message_id)
#     print(message)

# from memory import DB_FILE, get_connection

# print(DB_FILE)
# connection = get_connection()

# cursor = connection.cursor()

# cursor.execute('SELECT COUNT(*) FROM messages')

# count = cursor.fetchone()[0]

# print("Stored SQLite messages:", count)
# connection.close()

# from vector_memory import sync_memories

# updated_messages = [
#     (10001, "I enjoy learning Javascript"),
#     (10002, "I like building AI projects")
# ]

# print("FIRST RUN")
# sync_memories(updated_messages)

# print("SECOND RUN")
# sync_memories(updated_messages)

# from vector_memory import collection

# test_ids = [10001, 10002]

# string_ids = [str(message_id) for message_id in test_ids]

# collection.delete(ids=string_ids)


# syncing sqlite and chromadb
# from memory import get_user_messages
# from vector_memory import sync_memories

# messages = get_user_messages("Rahul")

# print(f"Found {len(messages)} messages")

# sync_memories(messages)


# from vector_memory import search_semantic_memory

# question = "What programming language I am learning?"

# res = search_semantic_memory(question)

# print(res)


# from memory import get_user_messages
# from vector_memory import sync_memories, search_semantic_memory

# participant = "Rahul"

# messages = get_user_messages(participant)

# sync_memories(messages, participant)

# results = search_semantic_memory("What programming language am I learning?", participant)

# print("\nRelevent messages:")

# for message in results:
#     print("-", message)


import unittest
from unittest.mock import patch, MagicMock

from vector_memory import (
    save_embedding,
    search_semantic_memory,
    delete_persona_memories,
)


class VectorMemoryTests(unittest.TestCase):

    @patch("vector_memory.get_embedding")
    @patch("vector_memory.collection")
    def test_save_embedding_uses_persona_id(self, mock_collection, mock_embedding):
        mock_embedding.return_value = [0.1, 0.2, 0.3]

        save_embedding(message_id=42, message="Hello!", persona_id=5)

        mock_collection.upsert.assert_called_once_with(
            ids=["persona:5:message:42"],
            embeddings=[[0.1, 0.2, 0.3]],
            documents=["Hello!"],
            metadatas=[{"persona_id": 5}],
        )

    @patch("vector_memory.get_embedding")
    @patch("vector_memory.collection")
    def test_search_filters_by_persona_id(self, mock_collection, mock_embedding):
        mock_embedding.return_value = [0.1, 0.2, 0.3]

        mock_collection.query.return_value = {"documents": [["Relevant message"]]}

        results = search_semantic_memory(question="Hello", persona_id=5)

        self.assertEqual(results, ["Relevant message"])

        mock_collection.query.assert_called_once_with(
            query_embeddings=[[0.1, 0.2, 0.3]],
            n_results=3,
            where={"persona_id": 5},
            include=["documents"],
        )

    @patch("vector_memory.collection")
    def test_delete_only_selected_persona(self, mock_collection):
        delete_persona_memories(persona_id=5)

        mock_collection.delete.assert_called_once_with(where={"persona_id": 5})
