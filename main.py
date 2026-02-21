import os
import requests
from flask import Flask, request

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

app = Flask(__name__)

# --- отправка сообщения в Telegram ---
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": chat_id,
        "text": text
    })

# --- запрос к OpenRouter ---
def ask_gpt(message):
    try:
        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "mistralai/mistral-7b-instruct",
                "messages": [
                    {"role": "system", "content": "Ты публичный AI помощник. Отвечай кратко и без форматирования."},
                    {"role": "user", "content": message}
                ]
            },
            timeout=60
        )

        answer = r.json()["choices"][0]["message"]["content"]
        return answer.replace("*", "").replace("#", "")

    except:
        return "Ошибка сервера. Попробуйте позже."

# --- проверка сервера ---
@app.route("/", methods=["GET"])
def home():
    return "Bot is running"

# --- webhook через токен ---
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    data = request.json

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        send_message(chat_id, "Бот работает ✅")

    return "ok", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
