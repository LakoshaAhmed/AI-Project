import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters

# ⛔ Insert your keys directly here
TELEGRAM_TOKEN = "8527912876:AAGrldzpVxcroBuRNcnKYpbMc0vksZ3IaI8"
OPENAI_API_KEY = "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"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I'm your AI bot powered by ChatGPT. Send me any question!")

def ask_chatgpt(prompt: str) -> str:
    url = "https://api.openai.com/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gpt-4.1",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    res = requests.post(url, json=data, headers=headers)
    res.raise_for_status()

    return res.json()["choices"][0]["message"]["content"]

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    try:
        ai_reply = ask_chatgpt(user_text)
        await update.message.reply_text(ai_reply)
    except Exception as e:
        await update.message.reply_text("Error: Something went wrong with ChatGPT.")
        print("Error:", e)

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
