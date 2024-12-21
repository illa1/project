import telebot
import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import threading


token = '7026411489:AAFC7FLRb6Yx2qnzqoSnsSsxXcPtGMxlW-Y'
bot = telebot.TeleBot(token)
filetext = 'bot_text.txt'
filenumber = 'bot_number.txt'

# --------- MESSAGES -----------------------------------------------------
def f1(v):
    try:
        int(v)
        return True
    except ValueError:
        return False

@bot.message_handler(content_types=['text'])
def is_text(message):
    if f1(message.text):
        filename = 'bot_number.txt'
    else:
        filename = 'bot_text.txt'
    with open(filename, 'a') as file:
        file.write(message.text + '\n')

    bot.send_message(message.chat.id, 'збережено до файлу!')

if __name__ == '__main__':
    bot.infinity_polling()