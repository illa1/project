import telebot
import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import threading


token = '7026411489:AAFC7FLRb6Yx2qnzqoSnsSsxXcPtGMxlW-Y'
bot = telebot.TeleBot(token)
filename = 'bot_message.txt'

# --------- MESSAGES -----------------------------------------------------
@bot.message_handler(content_types=['text'])
def is_text(message):
    with open(filename, 'a') as file:
        file.write(message.text + '\n')

    bot.send_message(message.chat.id, 'збережено до файлу!')

if __name__ == '__main__':
    bot.infinity_polling()