import telebot
import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy


token = '7026411489:AAFC7FLRb6Yx2qnzqoSnsSsxXcPtGMxlW-Y'
bot = telebot.TeleBot(token)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///example.sqlite"

db = SQLAlchemy(app)


class Base(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(), nullable=False)


@app.route('/')
def index():
    mes = Base.query.all()
    return render_template('index.html', mes=mes)


sticker_list = [
    'CAACAgIAAxkBAAO3Z0iqLLOSpaCz8_EVHM7uWxrxLD4AAgUAA8A2TxP5al-agmtNdTYE',
    'CAACAgIAAxkBAAO3Z0iqLLOSpaCz8_EVHM7uWxrxLD4AAgUAA8A2TxP5al-agmtNdTYE',
    'CAACAgIAAxkBAAO3Z0iqLLOSpaCz8_EVHM7uWxrxLD4AAgUAA8A2TxP5al-agmtNdTYE'
]


@bot.message_handler(content_types=['sticker'])
def handler_sticker(message):
    id = message.sticker.file_id
    em = message.sticker.emoji
    text = f"ІД стікара = ({id}). Емоджі = ({em})"
    bot.reply_to(message, text)


@bot.message_handler(commands=['f'])
def handler_f(message):
    current_path_app = os.path.abspath(__file__)
    current_path = os.path.dirname(current_path_app)
    my_file = os.path.join(current_path, 'sticker', 'f2.webp')

    with open(my_file, 'rb') as sticker:
        bot.send_sticker(message.chat.id, sticker)


# ------ TEXT
@bot.message_handler(content_types=['text'])
def is_text(message):
    if message.text == 'a':
        bot.send_sticker(message.chat.id, sticker_list[0])
        return True

    bot.send_message(message.chat.id, 'Текст')


if __name__ == '__main__':
    bot.infinity_polling()
