import ollama

response = ollama.embed(
    model="nomic-embed-text",
    input="I started learning python today."
)

embedding = response.embeddings[0]

print("Embedding generated successfully")

print("\nVector dimentions: ", len(embedding))

print("\nFirst 10 values:", embedding[:10])