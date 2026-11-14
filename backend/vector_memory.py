import chromadb
import ollama

client = chromadb.PersistentClient(path="../data/chroma_db")

collection = client.get_or_create_collection(
    name="chatpersona_memories"
)

def get_embedding(message, model):
    response = ollama.embed(model=model, input=message)
    return response["embeddings"][0]

def save_embedding(message_id, message):
    embedding = get_embedding(message, "nomic-embed-text")

    collection.add(
        ids = [str(message_id)],
        embeddings = [embedding]
    )