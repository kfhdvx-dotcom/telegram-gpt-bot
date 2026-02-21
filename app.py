from flask import Flask, request
import requests
import os

app = Flask(__name__)

# Получаем токены из переменных окружения Render
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

# Функция для отправки запроса в OpenRouter GPT
def ask_openrouter(message):
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {"role": "user", "content": message}
        ]
    }

    response = requests.post(url, headers=headers, json=data)
    # Получаем ответ от OpenRouter
    return response.json()["choices"][0]["message"]["content"]

# Основной маршрут webhook (обязательно совпадает с токеном)
@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    data = request.json

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        # Получаем ответ от OpenRouter
        reply = ask_openrouter(text)

        # Отправляем ответ пользователю в Telegram
        send_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(send_url, json={
            "chat_id": chat_id,
            "text": reply
        })

    return {"ok": True}

# Проверка работы сервиса
@app.route("/")
def home():
    return "Bot is running!"
