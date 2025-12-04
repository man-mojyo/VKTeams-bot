import logging
import os
import json
from bot.bot import Bot
from bot.handler import MessageHandler, StartCommandHandler,BotButtonCommandHandler
from dotenv import load_dotenv


load_dotenv()
TOKEN = os.getenv('TOKEN')


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log", encoding="utf-8"),  # лог в файл
        logging.StreamHandler()                            # лог в консоль
    ]
)

commands_list = ['/start', '/help']

def message_cb(bot, event):
    chat_id=event.from_chat
    msg_user = event.text
    logging.info(f"Получено сообщение от {chat_id}: \"{msg_user}\"")
    if msg_user and msg_user[0] != '/':
        msg_bot = 'Мне непонятно твое сообщение. Ты можешь использовать /start'
        bot.send_text(chat_id=event.from_chat, text=msg_bot)
    if msg_user[0] == '/' and msg_user not in commands_list:
        msg_bot = "Команда не найдена. Попробуй /start"
        bot.send_text(chat_id=event.from_chat, text=msg_bot)    
    

def start_cb(bot, event):
    chat_id=event.from_chat
    msg_user = event.text
    logging.info(f"Получено сообщение от {chat_id}: \"{msg_user}\"")
    bot.send_text(chat_id=event.from_chat, 
                  text="Привет, я бот-помощник в твоей работе.",
                  inline_keyboard_markup="{}".format(json.dumps([
                      [{"text": "Задачи на сегодня", "callbackData": "task_today", 'style': "base"}],
                      [{"text": "Календарь событий", "callbackData": "calendar", "style": "attention"}],
                      [{"text": "Отправить письмо", "callbackData": "call_back_id_3", "style": "primary"}],
                      [{"text": "Cделать рассылку", "callbackData": "call_back_id_4", "style": "base"}],
                      [{"text": "ИИ помощник", "callbackData": "call_back_id_5", "style": "primary"}]
                  ])))
def buttons_answer_cb(bot, event):
    callback_msg = event.data['callbackData']
    logging.info(f'{callback_msg}')

    if event.data['callbackData'] == "task_today":
        bot.send_text(chat_id=event.from_chat, 
                    text = '''<b>Список задач на сегодня:</b>
<ul>
  <li>Подготовить отчёт по продажам за неделю</li>
  <li>Проверить входящие письма и ответить на срочные</li>
  <li>Подготовить презентацию для встречи с клиентом</li>
  <li>Обновить внутреннюю документацию по проекту</li>
  <li>Провести код-ревью для коллеги</li>
</ul>
 ''', parse_mode = 'HTML')

    elif event.data['callbackData'] == "calendar":
        bot.send_text(chat_id=event.from_chat, 
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
        [{"text": "->", "callbackData": "next_days_in_week_1", 'style': "base"}]
                  ]))
    )
    elif event.data['callbackData'] == "next_days_in_week_1":
        bot.send_text(chat_id=event.from_chat, 
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
    inline_keyboard_markup="{}".format(json.dumps([
        [{"text": "->", "callbackData": "next_days_in_week_2", 'style': "base"}]
                  ]))
    )

    elif event.data['callbackData'] == "next_days_in_week_2":
        bot.send_text(chat_id=event.from_chat, 
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

 ''', parse_mode = 'HTML'
    )

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
