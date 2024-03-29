# This is my implementation for the Telegram API
import requests


class TelegramBot:
    def __init__(self, token):
        self.token = token
        self.api_url = f"https://api.telegram.org/bot{token}/"

    def send_message(self, chat: str, text: str):
        data = {"chat_id": chat, "text": text, "parse_mode": "markdown"}
        r = requests.post(f"{self.api_url}sendMessage", data=data)
        return r.json()
