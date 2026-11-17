import chromadb
import ollama
from memory import get_message_by_id
from pathlib import Path

#dynamic path
BASE_DIR = Path(__file__).resolve().parent.parent

Chroma_PATH = BASE_DIR / "data" / "chroma_db"

client = chromadb.PersistentClient(path=str(Chroma_PATH))

collection = client.get_or_create_collection(
    name="chatpersona_memories"
)

def get_embedding(message, model):
    response = ollama.embed(model=model, input=message)
    return response["embeddings"][0]

def save_embedding(message_id, message, participant):
    embedding = get_embedding(message, "nomic-embed-text")

    collection.add(
        ids = [str(message_id)],
        embeddings = [embedding],
        documents=[message],
        metadatas = [{"participant": participant}]
    )

#find ids of similar embeddings to user input text stored in chromadb
def get_similar_embeddings_ids(question,participant, model="nomic-embed-text" , n_results=3):
        #convert question(user message) to embeddings
        question_embedding = get_embedding(message=question, model=model)

        #find similar embeddings
        results = collection.query(
             query_embeddings=[question_embedding], #could be multiple embeddings
             n_results=n_results,
             where={"participant":participant}
        )

        return results["ids"][0]

#searching similar messages to user query by semantic search in chromadb
def search_semantic_memory(question, participant, n_results=3):
    #search chromadb for matching id
    message_ids = get_similar_embeddings_ids(
        question,
        participant,
        n_results = n_results
     )

    #retrieve messages from SQLite
    messages = []
    for message_id in message_ids:
         message = get_message_by_id(message_id)
         if message is not None:     #ignore missing messages
              messages.append(message)

    return messages     #return this message

#check if message-embedding exists in chroma
def embedding_exists(message_id):
     results = collection.get(ids=[str(message_id)])

     return bool(results["ids"])

#syncing chromadb to sqlite
def sync_memories(messages, participant):
     for message_id, sqlite_message in messages:
          print(f"Processing message ID: {message_id}")
          result = collection.get(
               ids = [str(message_id)],
               include = ["documents", "metadatas"]
          )
          if not result["ids"]:
               save_embedding(message_id, sqlite_message, participant)
               print(f"Added embedding: {message_id}")
               continue
          else:
               documents = result["documents"]

               chroma_message = documents[0] if documents else None

               updated = False

               if sqlite_message != chroma_message:
                    new_embedding = get_embedding(sqlite_message, model="nomic-embed-text")
                    collection.update(
                         ids = [str(message_id)],
                         embeddings=[new_embedding],
                         documents = [sqlite_message]
                    )
                    updated = True
                    print("Updated embedding")
               else:
                    print("Skipped embedding")

               metadata = result["metadatas"]

               chroma_metadata = metadata[0] if metadata else None

               if chroma_metadata is None or chroma_metadata.get("participant") != participant:
                    collection.update(
                         ids = [str(message_id)],
                         metadatas=[{"participant":participant}]
                    )
                    updated = True
                    print("Metadata updated successfully.")
               else:
                    print("Metadata not updated.")

               if not updated:
                    print("Skipped")

        