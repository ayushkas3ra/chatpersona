from vector_memory import save_embedding, collection

# save_embedding(1, "I love to code in python language.")

# print("Embedding saved successfully.")

result = collection.get(
    ids=['1'],
    include=["embeddings"]
)
print(result)