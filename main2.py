import telebot
import sqlite3

API_TOKEN = "7166981544:AAH2oX0DRvRwPQRhH2Kq2FRo8NCjxSNi8SI"

bot = telebot.TeleBot(API_TOKEN, parse_mode="HTML")

conn = sqlite3.connect('users.db', check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE,
    username TEXT
)
''')
conn.commit()

text_message = ""

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    username = message.from_user.username

    cursor.execute('''
    SELECT * FROM users WHERE user_id = ?
    ''', (user_id,))
    existing_user = cursor.fetchone()

    if existing_user:
        print(f"Пользователь {username} уже есть в базе данных")
    else:
        cursor.execute('''
        INSERT INTO users (user_id, username)
        VALUES (?, ?)
        ''', (user_id, username))
        conn.commit()
        print(f"Пользовватель {username} успешно добавлен в DB")

    bot.send_message(message.chat.id, "Добро пожаловать!")


@bot.message_handler(commands=['send'])
def handle_send(message):
    if message.from_user.id != 6704787842:
        bot.reply_to(message, "Ты кто? Пошел ты!!!")
        return

    bot.send_message(message.chat.id, 'Отправить текст для рассылки')
    bot.register_next_step_handler(message, process_text)

def process_text(message):
    global text_message
    text_message = message.text
    bot.send_message(message.chat.id, "Рассылка началась ->")

    send_broadcast()

def send_broadcast():
    global text_message
    cursor.execute('SELECT user_id FROM users')
    users = cursor.fetchall()

    for user in users:
        user_id = user[0]
        try:
            bot.send_message(user_id, text_message)
        except Exception as e:
            print(f"Ошибка пользователя {user_id}: {e}")
    text_message = ""




bot.polling()