import os
import telebot

API_TOKEN = os.getenv('API_TOKEN')  # Token from environment variable
OWNER_ID = int(os.getenv('OWNER_ID'))  # Owner ID from environment variable

bot = telebot.TeleBot(API_TOKEN, parse_mode="Markdown")  # Enable Markdown parsing

# Rest of your code remains the same...
# Maintain a set of active chat IDs
active_chats = set()


# Notify the owner whenever /info command is used
def notify_owner(user, chat_type, target_user=None, message_link=None):
    if chat_type == "private":
        notification = f"({user.first_name}), ({user.id}) is seeing their information."
    else:
        notification = f"{user.first_name} (@{user.username}) is searching information about @{target_user.username}.\n"
        notification += f"Message link: {message_link}"
    
    bot.send_message(OWNER_ID, notification)


# Track active chats
@bot.message_handler(func=lambda message: True)
def track_active_chats(message):
    active_chats.add(message.chat.id)


# /start command
@bot.message_handler(commands=['start'])
def start(message):
    user = message.from_user
    bot.send_message(
        message.chat.id,
        f"Hello @{user.username}, welcome to my Information bot. Hope you enjoy the service. "
        "Type /info to see your information privately. Type /runadd to run your advertisement in the bot."
    )


# /info command
@bot.message_handler(commands=['info'])
def info(message):
    user = message.from_user
    chat_id = message.chat.id
    
    if message.chat.type in ["group", "supergroup"]:
        bot_info = bot.get_chat_member(chat_id, bot.user.id)
        is_owner = (user.id == OWNER_ID)
        
        if bot_info.status not in ["administrator", "creator"] and not is_owner:
            bot.send_message(chat_id, "Please make me an admin to access user information.")
            return

        target_user = None
        if message.reply_to_message:
            target_user = message.reply_to_message.from_user
        elif message.entities and message.entities[0].type == "mention":
            username = message.text.split("@")[1].strip()
            try:
                target_user = bot.get_chat_member(chat_id, f"@{username}").user
            except:
                bot.send_message(chat_id, "User not found.")
                return
        
        if not target_user:
            target_user = user
        
        chat_id_stripped = str(chat_id).replace("-100", "")
        message_link = f"https://t.me/c/{chat_id_stripped}/{message.message_id}"
        
        notify_owner(user, "group", target_user, message_link)
        
        user_info = f"Userid: {target_user.id}\n" \
                    f"Username: @{target_user.username}\n" \
                    f"First name: {target_user.first_name}\n" \
                    f"Last name: {target_user.last_name or 'N/A'}\n" \
                    f"User's link: [click here](tg://openmessage?user_id={target_user.id})\n" \
                    f"Premium: {'yes' if target_user.is_premium else 'no'}\n" \
                    f"Language: {target_user.language_code}"
        
        if bot_info.status == "administrator" or is_owner:
            user_status = bot.get_chat_member(chat_id, target_user.id).status
            user_info += f"\nUser status: {user_status.capitalize()}"
        
        bot.send_message(chat_id, user_info)
    else:
        notify_owner(user, "private")
        bot.send_message(
            user.id,
            f"Userid: {user.id}\n"
            f"Username: @{user.username}\n"
            f"First name: {user.first_name}\n"
            f"Last name: {user.last_name or 'N/A'}\n"
            f"User's link: [click here](tg://openmessage?user_id={user.id})\n"
            f"Premium: {'yes' if user.is_premium else 'no'}\n"
            f"Language: {user.language_code}"
        )


# /runadd command
@bot.message_handler(commands=['runadd'])
def runadd(message):
    bot.send_message(message.chat.id, "Please contact @M_TM_A for running advertisements in the bot.")


# /broadcast command (Owner only)
@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    if message.from_user.id != OWNER_ID:
        bot.send_message(message.chat.id, "You are not authorized to use this command.")
        return
    
    if message.reply_to_message:
        text = message.reply_to_message.text
        failed_chats = []
        for chat_id in active_chats:
            try:
                bot.send_message(chat_id, text)
            except Exception as e:
                failed_chats.append(chat_id)
                print(f"Failed to send message to {chat_id}: {e}")
        
        bot.send_message(
            OWNER_ID,
            f"Broadcast completed. Failed to send to {len(failed_chats)} chats."
        )
    else:
        bot.send_message(message.chat.id, "Please reply to the message you want to broadcast.")


bot.polling()
