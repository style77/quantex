# This is my implementation for the Telegram API
import requests


class TelegramBot:
    def __init__(self, token):
        self.token = token
        self.api_url = "https://api.telegram.org/bot{}/".format(token)

    def send_message(self, chat: str, text: str):
        data = {"chat_id": chat, "text": text, "parse_mode": "markdown"}
        r = requests.post(self.api_url + "sendMessage", data=data)
        return r.json()
