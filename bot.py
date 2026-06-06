import telebot
from config import TOKEN


bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
        "Привет, я бот-подсказчик! Я помогу тебе искать новые и интересные пути для развития своей карьеры! /commands - список команд.")
    
@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id,
        "Просто напиши мне, что тебя интересует, и я постараюсь помочь тебе найти полезные ресурсы и советы для твоего карьерного роста!")
