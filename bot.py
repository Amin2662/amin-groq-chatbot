import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq
from collections import defaultdict

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL = "llama-3.1-70b-instant"

client = Groq(api_key=GROQ_API_KEY)

# حافظه برای هر کاربر
memory = defaultdict(list)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام! من چت‌بات هوش مصنوعی‌تم 🤖\nهر چی بگی جواب می‌دم و حرفاتو یادم می‌مونه!\nبرای پاک کردن حافظه بنویس /clear"
    )

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    memory[user_id] = []
    await update.message.reply_text("حافظه پاک شد! حالا از اول شروع کنیم 😊")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text

    memory[user_id].append({"role": "user", "content": user_message})

    # حداکثر ۲۰ پیام آخر نگه می‌داریم
    if len(memory[user_id]) > 20:
        memory[user_id] = memory[user_id][-20:]

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=memory[user_id],
            temperature=0.8,
            max_tokens=600
        )
        bot_reply = response.choices[0].message.content

        memory[user_id].append({"role": "assistant", "content": bot_reply})
        await update.message.reply_text(bot_reply)

    except Exception as e:
        await update.message.reply_text(f"خطایی پیش اومد: {str(e)}")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    print("ربات چت با حافظه فعال شد 🚀")
    app.run_polling()

if __name__ == "__main__":
    main()
