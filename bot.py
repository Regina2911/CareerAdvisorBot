import telebot
from telebot import types
from openai import OpenAI

from config import OPENROUTER_API_KEY, TOKEN
from database import create_table, save_user, get_user
from questions import quick_questions, deep_questions
from recommendations import get_recommendation


bot = telebot.TeleBot(TOKEN)

from config import TOKEN, OPENROUTER_API_KEY

client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)


# ---------------- БАЗА ----------------

create_table()

user_answers = {}
current_question = {}
deep_answers = {}
deep_question_index = {}
career_mode = {}

# ---------------- ИИ ----------------

def ask_ai(text):
    try:
        response = client.chat.completions.create(
            model="deepseek/deepseek-chat-v3-0324",
            #model="deepseek/deepseek-r1"
            temperature=0.3,
            messages=[{"role": "system", "content": 
"""
Ты профессиональный карьерный консультант.

Отвечай ТОЛЬКО на русском языке.

Никогда не смешивай русский и английский языки.
Никогда не генерируй случайные символы или бессмысленный текст.

Всегда оформляй ответ так:

🎯 Подходящие профессии
💡 Почему подходят
📚 Что изучить
🚀 План действий

Пиши красиво, структурированно и дружелюбно.
"""
},
                {"role": "user", "content": text}])

        return response.choices[0].message.content

    except Exception as e:
        print(e)
        return f"Ошибка: {e}"


# ---------------- START (КРАСИВЫЙ ЭКРАН) ----------------

@bot.message_handler(commands=['start'])
def start(message):

    text = (
        "👋 Привет!\n\n"
        "Я бот-помощник по карьере.\n\n"
        "Я помогу тебе:\n"
        "🎯 найти профессию\n"
        "🧠 пройти тест\n"
        "📊 узнать сильные стороны\n\n"
        "Выбери действие ниже 👇"
    )

    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(
        types.InlineKeyboardButton("📝 Пройти мини-тест", callback_data="test")
    )

    keyboard.add(
        types.InlineKeyboardButton("🧠 Глубокий тест", callback_data="deep_test")
    )

    keyboard.add(
        types.InlineKeyboardButton("🔎 Найти профессию", callback_data="career")
    )

    keyboard.add(
        types.InlineKeyboardButton("👤 Профиль", callback_data="profile")
    )

    bot.send_message(message.chat.id, text, reply_markup=keyboard)


# ---------------- КНОПКИ ----------------

@bot.callback_query_handler(func=lambda call: True)
def callback(call):

    chat_id = call.message.chat.id

    if call.data == "test":
        start_test(call.message)

    elif call.data == "deep_test":
        start_deep_test(call.message)

    elif call.data == "career":
        career_mode[chat_id] = True
        bot.send_message(chat_id, "Напиши, что тебе нравится (интересы, хобби, предметы) 👇")

    elif call.data == "profile":
        profile(call.message)


# ---------------- ТЕСТ 1 ----------------

@bot.message_handler(commands=['minitest'])
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

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

    for a in question["answers"]:
        keyboard.add(types.KeyboardButton(a))

    bot.send_message(chat_id, question["question"], reply_markup=keyboard)


# ---------------- ТЕСТ 2 ----------------

def start_deep_test(message):
    chat_id = message.chat.id

    deep_answers[chat_id] = []
    deep_question_index[chat_id] = 0

    bot.send_message(chat_id,
        "🧠 Сейчас я задам несколько вопросов. Отвечай своими словами.")

    send_deep_question(chat_id)


def send_deep_question(chat_id):

    index = deep_question_index[chat_id]

    if index >= len(deep_questions):
        finish_deep_test(chat_id)
        return

    bot.send_message(chat_id, deep_questions[index])



def finish_deep_test(chat_id):
    answers = deep_answers[chat_id]

    prompt = f"""
Ты профессиональный карьерный консультант.

Пользователь ответил на вопросы профориентационного теста:

{chr(10).join(answers)}

Сделай красивый и понятный отчёт.

Используй такой формат:

🎯 Подходящие профессии:
• профессия 1
• профессия 2
• профессия 3

💡 Почему тебе подходят эти профессии:
Напиши 2-3 предложения простым языком.

📚 Что стоит изучить:
• навык 1
• навык 2
• навык 3

🚀 С чего начать:
Дай 3 конкретных шага новичку.

Пиши дружелюбно, обращайся на "ты".
Не используй сложные термины.
"""

    result = ask_ai(prompt)

    bot.send_message(
    chat_id, "🎯 Результат глубокого анализа:\n\n" + result,
    reply_markup=types.ReplyKeyboardRemove())
        

    del deep_answers[chat_id]
    del deep_question_index[chat_id]


# ---------------- ОТВЕТЫ ----------------

@bot.message_handler(func=lambda message: True)
def handle_answers(message):

    chat_id = message.chat.id
    text = message.text

    # ТЕСТ 1
    if chat_id in current_question:

        user_answers[chat_id].append(text)
        current_question[chat_id] += 1

        ask_question(chat_id)
        return

    # ТЕСТ 2
    if chat_id in deep_question_index:

        deep_answers[chat_id].append(text)

        deep_question_index[chat_id] += 1

        send_deep_question(chat_id)

        return

    # ИИ
    if not text.startswith("/"):
        answer = ask_ai(text)
        bot.send_message(chat_id, answer)

# ---------------- ПРОФИЛЬ ----------------

@bot.message_handler(commands=['profile'])
def profile(message):

    user = get_user(message.chat.id)

    if not user:
        bot.send_message(message.chat.id, "Ты ещё не проходил тест.")
        return

    text = (
        f"📊 ТВОЙ ПРОФИЛЬ\n\n"
        f"Возраст: {user[1]}\n"
        f"Интересы: {user[2]}\n"
        f"Формат работы: {user[3]}\n"
        f"Сильная сторона: {user[4]}"
    )

    bot.send_message(message.chat.id, text)


def finish_test(chat_id):

    answers = user_answers[chat_id]

    recommendation = get_recommendation(answers)

    save_user(
        chat_id,
        answers[0],
        answers[1],
        answers[3],
        answers[4]
    )

    text = (
        f"🎯 ТВОЁ НАПРАВЛЕНИЕ\n\n"
        f"{recommendation}\n\n"
        f"Теперь нажми /career и попробуй ИИ 🔎"
    )

    bot.send_message(
    chat_id,
    text,
    reply_markup=types.ReplyKeyboardRemove())
    del user_answers[chat_id]
    del current_question[chat_id]


bot.infinity_polling()