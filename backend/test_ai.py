from ollama import chat

response = chat(
    model = "qwen3:1.7b",
    messages = [
        {
            "role":"user",
            "content":"Reply casually to 'Bro what are you doing?' "
        }
    ]
)
print("\nQwen response:")
print(response.message.content)