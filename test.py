import logging
import os
import json
from bot.bot import Bot
from bot.handler import MessageHandler, StartCommandHandler,BotButtonCommandHandler
from dotenv import load_dotenv
from ai_agent import VKAgent
import requests

load_dotenv()
TOKEN = os.getenv('TOKEN')
ai_agent = VKAgent()
user_data = {}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log", encoding="utf-8"),  # лог в файл
        logging.StreamHandler()                            # лог в консоль
    ]
)

commands_list = ['/start']

def send_picture(bot, event):
    # Получаем upload URL
    chat_id = event.from_chat
    print('send_picture')
    upload_url = bot.get_file_upload_url(chat_id=chat_id, file_type="image")

    # Загружаем файл
    with open('images\photo_2025-12-05_05-52-20.jpg', "rb") as f:
        res = requests.post(upload_url, files={"file": f}).json()

    file_id = res["fileId"]

    # Отправляем файл пользователю
    bot.send_file(
        chat_id=chat_id,
        file_id=file_id,
        file_type="image"
    )

def main():
        bot = Bot(token=TOKEN)
        bot.dispatcher.add_handler(StartCommandHandler(callback=send_picture))
        logging.info("Бот запущен")
        bot.start_polling()
        bot.idle()
    
if __name__ == '__main__':
    main()