from flask import Flask, request
import requests
import os

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

# Словарь для хранения диалогов пользователей
user_chats = {}

# Функция для отправки запроса в OpenRouter GPT
def ask_openrouter(messages):
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "openai/gpt-4o-mini",
        "messages": messages
    }

    response = requests.post(url, headers=headers, json=data)
    return response.json()["choices"][0]["message"]["content"]

@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    data = request.json

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        # Инициализируем диалог пользователя, если его нет
        if chat_id not in user_chats:
            user_chats[chat_id] = []

        # Добавляем сообщение пользователя в память
        user_chats[chat_id].append({"role": "user", "content": text})

        # Получаем ответ от OpenRouter GPT, используя всю историю
        reply = ask_openrouter(user_chats[chat_id])

        # Добавляем ответ бота в память
        user_chats[chat_id].append({"role": "assistant", "content": reply})

        # Отправляем ответ пользователю
        send_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(send_url, json={
            "chat_id": chat_id,
            "text": reply
        })

    return {"ok": True}

@app.route("/")
def home():
    return "Bot is running!"
