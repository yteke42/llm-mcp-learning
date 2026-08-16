import json
import urllib.request


class LLM:
    def __init__(
        self,
        model="qwen3:8b",
        url="http://localhost:11434/api/chat"
    ):
        self.model = model
        self.url = url
        self.messages = []

    def ask(self, prompt):
        self.messages.append({
            "role": "user",
            "content": prompt
        })

        data = {
            "model": self.model,
            "messages": self.messages,
            "stream": False
        }

        request = urllib.request.Request(
            self.url,
            data=json.dumps(data).encode("utf-8"),
            headers={
                "Content-Type": "application/json"
            }
        )

        with urllib.request.urlopen(request) as response:
            result = json.loads(response.read())

        answer = result["message"]["content"]

        self.messages.append({
            "role": "assistant",
            "content": answer
        })

        return answer