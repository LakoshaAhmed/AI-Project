import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters
from openai import OpenAI
import json

TELEGRAM_TOKEN = "8527912876:AAGrldzpVxcroBuRNcnKYpbMc0vksZ3IaI8" 
OPENAI_API_KEY = "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"  
ENDPOINT = "https://models.github.ai/inference"  
MODEL_NAME = "openai/gpt-4o"  

client = OpenAI(base_url=ENDPOINT, api_key=OPENAI_API_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I'm your AI bot powered by ChatGPT. Send me any question!")

async def ask_chatgpt(prompt: str) -> str:
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=1.0,
            top_p=1.0,
            max_tokens=1000,
            model=MODEL_NAME
        )

        return response.choices[0].message.content

    except Exception as e:
        print(f"Error: {e}")
        return f"Error: Something went wrong with the OpenAI API. {e}"

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    try:
        ai_reply = await ask_chatgpt(user_text)
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
