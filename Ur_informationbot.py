import os
import telebot

# Load environment variables
API_KEY = os.getenv('BOT_API_KEY')     # Telegram bot API key
OWNER_ID = os.getenv('OWNER_ID')         # Your Telegram user ID (e.g. for authorized commands)

# Initialize the bot
bot = telebot.TeleBot(API_KEY)

# Command handler for `/start`
@bot.message_handler(commands=['start'])
def start(message):
    user = message.from_user
    bot.send_message(
        message.chat.id,
        f"Hello @{user.username}, welcome to the Information Bot! Type /info to see your information."
    )

# Command handler for `/info`
@bot.message_handler(commands=['info'])
def info(message):
    user = message.from_user
    bot.send_message(
        message.chat.id,
        f"UserID: {user.id}\nUsername: @{user.username}\nFirst Name: {user.first_name}"
    )

# Command handler for `/runadd` (Run advertisement)
@bot.message_handler(commands=['runadd'])
def run_add(message):
    bot.send_message(
        message.chat.id, 
        "Please contact @YourSupport for advertisements."
    )

# Command handler for `/broadcast` (Only for authorized users)
@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    if message.from_user.id == int(OWNER_ID):
        # Broadcast message logic here
        bot.send_message(message.chat.id, "This is a broadcast message!")
    else:
        bot.send_message(message.chat.id, "You are not authorized to use this command.")

# Keep the bot running with long polling
bot.polling()
