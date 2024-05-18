import logging

import telebot


# Telegram bot token and chat ID
TELEGRAM_TOKEN = 'your-telegram-bot-token'
CHAT_ID = 'your-chat-id'

# Initialize Telegram bot
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Function to send Telegram notification


def send_telegram_message(message: str):
    try:
        bot.send_message(CHAT_ID, message)
        logging.info(f"[+] Sent Telegram message: {message}")
        print(f"[+] Sent Telegram message: {message}")
    except Exception as e:
        logging.error(f"[+] Failed to send Telegram message: {e}")
        print(f"[+] Failed to send Telegram message: {e}")
