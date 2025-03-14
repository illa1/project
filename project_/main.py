import threading
import config as c
from SQliteManager import SQLNote
import telebot
import time
import sqlite3
import re
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime as dt

bot = telebot.TeleBot(c.BOT_TOKEN)

# ---------------------- SQLITE ------------------------------
# db = sqlite3.connect('notebook.db')
# cur = db.cursor()
#
# cur.execute('''CREATE TABLE users (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         chat_id INTEGER NOT NULL,
#         name TEXT DEFAULT 'Невідомий',
#         deleted INTEGER DEFAULT 0
#     )''')
# db.commit()
#
# cur.execute('''CREATE TABLE IF NOT EXISTS notes (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         user_id INTEGER NOT NULL,
#         title TEXT NOT NULL,
#         content TEXT DEFAULT '',
#         notification DATETIME DEFAULT CURRENT_TIMESTAMP,
#         is_send INTEGER DEFAULT 0,
#         deleted INTEGER DEFAULT 0
#     )''')
# db.commit()


# ---------------------- FUNCTION ---------------------------
def get_db_cursor():
    return SQLNote(c.DB_NAME)

def send_text_message():
    while True:
        notes_id_list = []
        print('message')
        with get_db_cursor() as cur:
            cur.execute('''
                SELECT users.chat_id, notes.title, notes.content, notes.notification, notes.id
                FROM notes
                INNER JOIN users ON notes.user_id = users.id
                WHERE notes.is_send = 0 AND notes.deleted = 0 AND notes.notification < datetime('now')
                ''')
            rows = cur.fetchall()
            print('rows')

            for r in rows:
                notes_id_list.append(r[4])
                message = "Нагадування!\n" + r[3] + '\n' + r[1] + '\n' + r[2]
                bot.send_message(r[0], message)
                time.sleep(1)

            id_str = ", ".join(['?'] * len(notes_id_list))
            cur.execute(f"UPDATE notes SET is_send = 1 WHERE id IN ({id_str})", notes_id_list)

        time.sleep(60)

def bot_start(message):
    print(message)
    with get_db_cursor() as cur:
        cur.execute("SELECT chat_id FROM users WHERE chat_id='%d'" % message.chat.id)
        row = cur.fetchone()

        if not row:
            cur.execute(f"INSERT INTO users (chat_id, name) VALUES ('{message.chat.id}', '{message.from_user.username}')")
            bot.send_message(message.chat.id, f'Користувача [{message.from_user.username}] додано')
        else:
            bot.send_message(message.chat.id, 'Ви вже підписалися на цього бота')

def bot_add_note(message):
    bot.send_message(message.chat.id, 'Введіть нотатку')
    bot.register_next_step_handler(message, bot_add_title)

def bot_add_title(message):
    with get_db_cursor() as cur:
        cur.execute(f"SELECT id FROM users WHERE chat_id={int(message.chat.id)}")
        row = cur.fetchone()

        if row:
            cur.execute("INSERT INTO notes (user_id, title) VALUES (?, ?)",
                        (row[0], message.text))
            bot.send_message(message.chat.id, 'нотатку додано')
        else:
            bot.send_message(message.chat.id, 'Немає користувача :(')

def all_notes(message):
    with get_db_cursor() as cur:
        cur.execute(f"SELECT id FROM users WHERE chat_id={int(message.chat.id)}")
        row = cur.fetchone()

        if row:
            cur.execute(f"SELECT id, title, notification From notes WHERE deleted=0 AND user_id={row[0]}")
            rows = cur.fetchall()

            notes = ''
            for r in rows:
                notes += f"/edit_{r[0]}: {r[1]}. [{r[2]}]\n"
            if notes:
                bot.send_message(message.chat.id,'Список нотаток:\n' + notes)
            else:
                bot.send_message(message.chat.id, 'Нотаток немає')

def edit_note(message, note_id):
    keyboard = InlineKeyboardMarkup()
    b1 = InlineKeyboardButton('заголовок', callback_data='title_' + note_id)
    b2 = InlineKeyboardButton('опис', callback_data='content_' + note_id)
    b3 = InlineKeyboardButton('час', callback_data='notification_' + note_id)
    b4 = InlineKeyboardButton('видалити', callback_data='delete_' + note_id)
    keyboard.add(b1, b2, b3)
    keyboard.add(b4)

    bot.send_message(message.chat.id, f'[{note_id}] Редагуваня:', reply_markup=keyboard)

def delete_note(call, note_id):
    with get_db_cursor() as cur:
        cur.execute(f"UPDATE notes SET deleted=1 WHERE id={int(note_id)}")

        if cur.rowcount > 0:
            bot.send_message(call.message.chat.id, 'Нотатка видалена')
        else:
            bot.send_message(call.message.chat.id, 'Помилка :(')

def title_note(call, note_id):
    if hasattr(call.message, 'message_id'):
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

    bot.send_message(call.message.chat.id, 'Введіть новий заголовок')
    bot.register_next_step_handler_by_chat_id(call.message.chat.id, save_title_note, note_id)

def save_title_note(message, note_id):
    with get_db_cursor() as cur:
        cur.execute(f"UPDATE notes SET title=? WHERE id= ?", (message.text, note_id))

        if cur.rowcount > 0:
            bot.send_message(message.chat.id, 'Нотатка оновлена')
        else:
            bot.send_message(message.chat.id, 'Помилка :(')

def content_note(call, note_id):
    pass

def notification_note(call, note_id):
    if hasattr(call.message, 'message_id'):
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

    m = """Введіть новий час у такому форматі:
    *день.місяць.рік години:хвилини*
    приклад `25.01.2025 12:00`
    """
    bot.send_message(call.message.chat.id, m, parse_mode='Markdown')
    bot.register_next_step_handler_by_chat_id(call.message.chat.id, save_notification_note, note_id)

def save_notification_note(message, note_id):
    try:
        original_data = dt.strptime(message.text, "%d.%m.%Y %H:%M")

        notification = original_data.strftime("%Y-%m-%d %H:%M:00")
        print(notification)
        with get_db_cursor() as cur:
            cur.execute(f"UPDATE notes SET notification=? WHERE id= ?", (notification, note_id))
            cur.execute(f"UPDATE notes SET is_send = 0 WHERE id= ?", (note_id,))
            if cur.rowcount > 0:
                bot.send_message(message.chat.id, 'час оновлена')
            else:
                bot.send_message(message.chat.id, 'Помилка :(')
    except Exception:
        bot.send_message(message.chat.id, f'Помилка :(\n неправельний формат')
# ---------------------- MESSAGE-HANDLERS --------------------

# start - підписатися
# add - додати
# all - показати всі нотатки
# help - вивести підказки
# end - відписатися

@bot.message_handler(commands=['start', 'add', 'help', 'end', 'all'])
def bot_commands(message):
    if '/start' == message.text:
        bot_start(message)
    elif '/add' == message.text:
        bot_add_note(message)
    elif '/all' == message.text:
        all_notes(message)

@bot.message_handler(regexp=r"^\/edit_\d+$")
def handler_edit_id(message):
    match = re.match(r"^\/edit_(\d+)$", message.text)

    if match:
        edit_note(message, match.group(1))


@bot.callback_query_handler(func=lambda call: True)
def handler_note_action(call):
    callback_data = call.data.split('_')
    if 2 == len(callback_data):
        if callback_data[0] == 'delete':
            delete_note(call,callback_data[1])
        elif callback_data[0] == 'title':
            title_note(call,callback_data[1])
        elif callback_data[0] == 'content':
            content_note(call,callback_data[1])
        elif callback_data[0] == 'notification':
            notification_note(call,callback_data[1])


@bot.message_handler(content_types=['text'])
def text_message(message):
    bot.send_message(message.chat.id, 'працює')



if __name__ == '__main__':
    thread = threading.Thread(target=send_text_message)
    thread.start()

    bot.infinity_polling()