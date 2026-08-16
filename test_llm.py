import json
import urllib.request

url = "http://localhost:11434/api/chat"

data = {
    "model": "qwen3:8b",
    "messages": [
        {
            "role": "user",
            "content": "MCP nedir? Kısaca açıkla."
        }
    ],
    "stream": False
}

request = urllib.request.Request(
    url,
    data=json.dumps(data).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)

with urllib.request.urlopen(request) as response:
    result = json.loads(response.read())

print(result["message"]["content"])