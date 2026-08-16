from ollama import chat

response = chat(
    model="qwen3:8b",
    messages=[
        {
            "role": "user",
            "content": "MCP nedir? (Model Context Protocol)"
        }
    ]
)

print(response.message.content)