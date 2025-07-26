import dotenv
dotenv.load_dotenv()

from app import bot
import app.handlers

if __name__ == "__main__":
    print("Bot is starting...")
    bot.infinity_polling()