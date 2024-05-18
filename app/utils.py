import logging
import os
import telebot
from dotenv import load_dotenv


load_dotenv()


# Telegram bot token and chat ID
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

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
