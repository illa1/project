import telebot


token = '7026411489:AAFC7FLRb6Yx2qnzqoSnsSsxXcPtGMxlW-Y'
bot = telebot.TeleBot(token)


# --- TEXT ---

@bot.message_handler(content_types=['text'])
def test_text(message):
    bot.send_message(message.chat.id, message.text + '\n[Бот працює]')



if __name__ == '__main__':
    bot.infinity_polling()
