import requests

BASE_URL = "https://agent.timeweb.cloud/api/v1/cloud-ai/agents/1334ab21-54e7-469a-8b3d-f59ba6b6e257/v1"
API_KEY = 'eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCIsImtpZCI6IjFrYnhacFJNQGJSI0tSbE1xS1lqIn0.eyJ1c2VyIjoicHQ2OTEwNTEiLCJ0eXBlIjoiYXBpX2tleSIsImFwaV9rZXlfaWQiOiIwY2U2ZjEwYy1hNmQ2LTRkYzQtOGYzMS0yYTY0ODEyOWQxYjMiLCJpYXQiOjE3NjQ4NzcwMzl9.obeH2wPNk1r_eBKj95hEmt1Rft_pvQbGEzuKyo7nUEz_jouoJynZ0fpR2x0SgfZPQX8OgRSqolEh4X9ezzTTQFNuKNQ1MBtY3Smd7dC911_18wSc2x0mZIogPSSJRlFHqKJeb-5qZwGOioM2kn4D4MC3HXd7EcMhNiuyycRNRij4FIsC5B2yJsp2J2lXH5c4VCzp0ME-nUO7eoVqKM1kD1JboIHLHY6ziGU0vuExMd_LPspJRaaoRxetcyFwIHIkwakgLIDhBfY4YCTFi4YH1N7O_d6wO3VvSyHOeSwEJPh6riw4FajLb7seZbqp6bW2ZpIYEt6AwVUUDohDglUeJpxkJRhJaWpJaxDMTSwu3jvLpbsGPw75nPdBgf93-PSqfjiB1XrVHCucZjsWBWMBv48T5cbjQOgMSF6-d1R5DWqx2JbFquGLzZSMLgWrrpZHnOr4Uuzubq9UQ-YLtnvTkcydA2lJDLG9RSBkcJz8BUNRTXWSgK1C3Ki-Oo00m56T'
MODEL = "gpt-5o-mini"

class VKAgent:
    def __init__(self):
        self.url = f"{BASE_URL}/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        }
        self.model = MODEL
        self.history = []  # для хранения контекста, если нужно

    def ask(self, prompt: str) -> str:
        # Добавляем в историю, чтобы можно было расширить контекст
        self.history.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model,
            "messages": self.history,  # можно использовать только [{"role": "user", "content": prompt}] для безконтекстного общения
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