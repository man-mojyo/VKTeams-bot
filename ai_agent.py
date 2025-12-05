import requests

BASE_URL = "https://agent.timeweb.cloud/api/v1/cloud-ai/agents/1334ab21-54e7-469a-8b3d-f59ba6b6e257/v1"
API_KEY = 'API-KEY'
MODEL = "gpt-5o-mini"

class VKAgent:
    def __init__(self):
        self.url = f"{BASE_URL}/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        }
        self.model = MODEL
        self.history = []  

    def ask(self, prompt: str) -> str:
        
        self.history.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model,
            "messages": self.history,  
        }

        try:
            resp = requests.post(self.url, json=payload, headers=self.headers, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            answer = data["choices"][0]["message"]["content"]
            
            # Добавляем ответ агента в историю
            self.history.append({"role": "assistant", "content": answer})
            return answer
        except requests.exceptions.RequestException as e:
            return f"Произошла ошибка при обращении к агенту: {e}"


if __name__ == "__main__":
    agent = VKAgent()
    print(agent.ask("Напиши слово \"Да\""))