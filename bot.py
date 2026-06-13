import telebot
from telebot import types

from config import TOKEN
from database import create_table, save_user, get_user
from questions import quick_questions
from recommendations import get_recommendation


bot = telebot.TeleBot(TOKEN)

create_table()

user_answers = {}
current_question = {}


@bot.message_handler(commands=['start'])
def start(message): bot.send_message(message.chat.id, 
        "Привет, я бот-подсказчик! Я помогу тебе искать новые и интересные пути для развития своей карьеры! /commands - список команд.")


@bot.message_handler(commands=['commands']) 
def commands(message): bot.send_message(message.chat.id, 
        "Список команд:\n/test - мини-тест \n/deep_test - расширенный список вопросов \n/profile - показать сохранённые ответы \n/recommendations - рекомендации по развитию карьеры")


def create_keyboard(options):

    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        one_time_keyboard=True
    )

    for option in options:
        keyboard.add(
            types.KeyboardButton(option)
        )

    return keyboard


@bot.message_handler(commands=['test'])
def start_test(message):

    chat_id = message.chat.id

    user_answers[chat_id] = []
    current_question[chat_id] = 0

    ask_question(chat_id)


def ask_question(chat_id):

    index = current_question[chat_id]

    if index >= len(quick_questions):
        finish_test(chat_id)
        return

    question = quick_questions[index]

    keyboard = create_keyboard(
        question["answers"]
    )

    bot.send_message(
        chat_id,
        question["question"],
        reply_markup=keyboard
    )


@bot.message_handler(commands=['profile'])
def profile(message):

    user = get_user(message.chat.id)

    if not user:

        bot.send_message(
            message.chat.id,
            "Вы ещё не проходили тест."
        )

        return

    text = (
        f"Возраст: {user[1]}\n"
        f"Интересы: {user[2]}\n"
        f"Формат работы: {user[3]}\n"
        f"Сильная сторона: {user[4]}"
    )

    bot.send_message(
        message.chat.id,
        text
    )


@bot.message_handler(func=lambda message: True)
def handle_answers(message):

    chat_id = message.chat.id

    if chat_id not in current_question:
        return

    user_answers[chat_id].append(
        message.text
    )

    current_question[chat_id] += 1

    ask_question(chat_id)


def finish_test(chat_id):

    answers = user_answers[chat_id]

    recommendation = get_recommendation(
        answers
    )

    save_user(
        chat_id,
        answers[0],
        answers[1],
        answers[3],
        answers[4]
    )

    text = (
        f"🎯 Ваше направление:\n\n"
        f"{recommendation}\n\n"
        f"Используйте /profile чтобы посмотреть результаты."
    )

    bot.send_message(
        chat_id,
        text
    )

    del user_answers[chat_id]
    del current_question[chat_id]


bot.infinity_polling()