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



def message_cb(bot, event):
    chat_id=event.from_chat
    msg_user = event.text
    if 'AI_agent' not in user_data.get(chat_id, {}):

        user_data.setdefault(chat_id, {})['AI_agent'] = False

    logging.info(f"Получено сообщение от {chat_id}: \"{msg_user}\"")
    print(user_data[chat_id]['AI_agent'])
    if user_data[chat_id]['AI_agent'] == True:

        msg_bot = ai_agent.ask(msg_user)
        msg_id =bot.send_text(chat_id=event.from_chat, text=msg_bot,inline_keyboard_markup="{}".format(json.dumps([
        [{"text": "Стартовое меню", "callbackData": "start_menu", 'style': "attention"}]
                  ])) 
                  ).json()['msgId']
        user_data[chat_id]["main_msg_id"] = msg_id        

    elif msg_user and msg_user[0] != '/':
        msg_bot = 'Мне непонятно твое сообщение.'
        msg_id =bot.send_text(chat_id=event.from_chat, text=msg_bot,inline_keyboard_markup="{}".format(json.dumps([
        [{"text": "Стартовое меню", "callbackData": "start_menu", 'style': "attention"}]
                  ])) 
                  ).json()['msgId']
        user_data[chat_id]["main_msg_id"] = msg_id      

    elif msg_user[0] == '/' and msg_user not in commands_list:
        msg_bot = "Команда не найдена. Попробуй /start"
        msg_id =bot.send_text(chat_id=event.from_chat, text=msg_bot,inline_keyboard_markup="{}".format(json.dumps([
        [{"text": "Стартовое меню", "callbackData": "start_menu", 'style': "attention"}]
                  ])) 
                  ).json()['msgId']
        user_data[chat_id]["main_msg_id"] = msg_id     

    

def start_cb(bot, event):
    chat_id=event.from_chat
    msg_user = event.text
    if chat_id not in user_data:
        user_data[chat_id] = {}
    user_data.setdefault(chat_id, {})['AI_agent'] = False

    logging.info(f"Получено сообщение от {chat_id}: \"{msg_user}\"")
    msg_id =bot.send_text(chat_id=event.from_chat, 
                  text="Привет, я бот-помощник в твоей работе.",
                  inline_keyboard_markup="{}".format(json.dumps([
                      [{"text": "Задачи на сегодня", "callbackData": "task_today", 'style': "base"}],
                      [{"text": "Календарь событий", "callbackData": "calendar", "style": "attention"}],
                      [{"text": "Отправить письмо", "callbackData": "call_back_id_3", "style": "primary"}],
                      [{"text": "Cделать рассылку", "callbackData": "call_back_id_4", "style": "base"}],
                      [{"text": "ИИ помощник", "callbackData": "AI_agent", "style": "primary"}]
                  ]))).json()['msgId']
    user_data[chat_id]["main_msg_id"] = msg_id
                  
def buttons_answer_cb(bot, event):
    callback_msg = event.data['callbackData']
    chat_id = event.from_chat
    logging.info(f'{callback_msg}')
    msg_id = user_data[chat_id]["main_msg_id"]
    if event.data['callbackData'] == "task_today":

        bot.edit_text(chat_id=event.from_chat, msg_id=msg_id, 
                    text = '''
<b>📌 Задачи на сегодня</b>
''',     inline_keyboard_markup="{}".format(json.dumps([
        [{"text": "Отчёт по продажам за неделю", "callbackData": "task_ok", 'style': "base"}],
        [{"text": "Проверить почту и ответить на срочные письма", "callbackData": "task_ok", 'style': "base"}],
        [{"text": "Подготовить презентацию к встрече с клиентом", "callbackData": "task_ok", 'style': "base"}],
        [{"text": "Обновить документацию по проекту", "callbackData": "task_ok", 'style': "base"}],
        [{"text": "Провести код-ревью", "callbackData": "task_ok", 'style': "base"}],
        [{"text": "Стартовое меню", "callbackData": "start_menu", 'style': "attention"}]
                  ])), parse_mode = 'HTML')

    elif event.data['callbackData'] == "calendar":
        bot.edit_text(chat_id=event.from_chat, msg_id=msg_id,
                    text = '''
<b>📅 Понедельник, 2 декабря 2025</b>
<ul>
  <li>09:00 — Утреннее совещание команды</li>
  <li>11:00 — Звонок с клиентом «Проект А»</li>
  <li>15:00 — Код-ревью по проекту «C»</li>
</ul>

<b>📅 Вторник, 3 декабря 2025</b>
<ul>
  <li>10:00 — Митинг по проекту «B»</li>
  <li>14:00 — Совещание с руководством</li>
  <li>16:00 — Код-ревью коллег</li>
</ul>
 ''', parse_mode = 'HTML',
    inline_keyboard_markup="{}".format(json.dumps([
        [{"text": "->", "callbackData": "next_days_in_week_1", 'style': "base"}],
        [{"text": "Стартовое меню", "callbackData": "start_menu", 'style': "attention"}]
                  ]))
    )
    elif event.data['callbackData'] == 'AI_agent':
        user_data[chat_id]['AI_agent'] = True
        bot.edit_text(chat_id=event.from_chat, msg_id=msg_id,
                    text = '''
Привет! Я ИИ-помощник этого бота, готов помочь с работой в VK Workspace и VKTeams. \nЗадавай свои вопросы!
 ''', parse_mode = 'HTML',
    inline_keyboard_markup="{}".format(json.dumps([
        [{"text": "Стартовое меню", "callbackData": "start_menu", 'style': "attention"}]
                  ]))
    )
    elif event.data['callbackData'] == "next_days_in_week_1":
        bot.edit_text(chat_id=event.from_chat,msg_id=msg_id, 
                    text = '''
<b>📅 Среда, 4 декабря 2025</b>
<ul>
  <li>09:30 — Встреча с подрядчиком</li>
  <li>11:00 — Митинг по проекту «A»</li>
  <li>15:00 — Код-ревью по проекту «D»</li>
</ul>

<b>📅 Четверг, 5 декабря 2025</b>
<ul>
  <li>10:00 — Совещание команды</li>
  <li>13:00 — Митинг с клиентом «Проект B»</li>
  <li>16:00 — Код-ревью</li>
</ul>
 ''', parse_mode = 'HTML',
    inline_keyboard_markup="{}".format(json.dumps([[
        {"text": "<-", "callbackData": "calendar", 'style': "base"},
        {"text": "->", "callbackData": "next_days_in_week_2", 'style': "base"}],
        [{"text": "Стартовое меню", "callbackData": "start_menu", 'style': "attention"}]
        
                  ]))
    )
    elif event.data['callbackData'] == "next_days_in_week_2":
        bot.edit_text(chat_id=event.from_chat,msg_id=msg_id,
                    text = '''
<b>📅 Пятница, 6 декабря 2025</b>
<ul>
  <li>09:00 — Утренний статус-апдейт</li>
  <li>11:00 — Митинг по проекту «C»</li>
  <li>14:00 — Итоговое код-ревью на неделю</li>
</ul>

<b>📅 Суббота, 7 декабря 2025</b>
<ul>
  <li>10:00 — Совещание по планированию следующей недели</li>
  <li>13:00 — Код-ревью выполненных задач</li>
</ul>

<b>📅 Воскресенье, 8 декабря 2025</b>
<ul>
  <li>11:00 — Подготовка отчётов на следующую неделю</li>
  <li>14:00 — Планирование митингов и задач</li>
</ul>

 ''',
     inline_keyboard_markup="{}".format(json.dumps([
        [{"text": "<-", "callbackData": "next_days_in_week_1", 'style': "base"}],
        [{"text": "Стартовое меню", "callbackData": "start_menu", 'style': "attention"}]
  
                  ])),
   parse_mode = 'HTML'
    )
    elif event.data['callbackData'] == "start_menu":
            bot.edit_text(chat_id=event.from_chat,msg_id=msg_id,
                  text="Привет, я бот-помощник в твоей работе.",
                  inline_keyboard_markup="{}".format(json.dumps([
                      [{"text": "Задачи на сегодня", "callbackData": "task_today", 'style': "base"}],
                      [{"text": "Календарь событий", "callbackData": "calendar", "style": "attention"}],
                      [{"text": "Отправить письмо", "callbackData": "call_back_id_3", "style": "primary"}],
                      [{"text": "Cделать рассылку", "callbackData": "call_back_id_4", "style": "base"}],
                      [{"text": "ИИ помощник", "callbackData": "AI_agent", "style": "primary"}]
                  ])))
    
        

def main():
    bot = Bot(token=TOKEN)
    bot.dispatcher.add_handler(StartCommandHandler(callback=start_cb))
    bot.dispatcher.add_handler(MessageHandler(callback=message_cb))
    bot.dispatcher.add_handler(BotButtonCommandHandler(callback=buttons_answer_cb))
    logging.info("Бот запущен")
    bot.start_polling()
    bot.idle()
    
if __name__ == '__main__':
    main()
