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


#syncing sqlite and chromadb
from memory import get_user_messages
from vector_memory import sync_memories

messages = get_user_messages("Rahul")

print(f"Found {len(messages)} messages")

sync_memories(messages)