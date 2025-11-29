import nest_asyncio
import logging
import asyncio
from telethon import TelegramClient, events
from openai import OpenAI
import os 


API_ID = 1234567 # (Integer)
API_HASH = '257cc05bcc9c656e2ac21e6cf7175f2d' #  (String)
BOT_TOKEN = '8527912876:AAGrldzpVxcroBuRNcnKYpbMc0vksZ3IaI8' 
OPENAI_API_KEY = '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' # Your OpenAI API Key (String)

logging.basicConfig(level=logging.INFO)

client = TelegramClient('bot', API_ID, API_HASH)


ai = OpenAI(api_key=OPENAI_API_KEY)


async def main():
    await client.start(bot_token=BOT_TOKEN)

    @client.on(events.NewMessage(pattern='/start'))
    async def start_handler(event):
        await event.respond("Hello! I am Hackers Realm AI Bot. How can I assist you today?")
        logging.info(f'/start from {event.sender_id}')

    @client.on(events.NewMessage(pattern='/info'))
    async def info_handler(event):
        await event.respond("This AI Chatbot is created in Python with OpenAI API.")
        logging.info(f'/info from {event.sender_id}')

    @client.on(events.NewMessage(pattern='/help'))
    async def help_handler(event):
        await event.respond(
            "Commands:\n"
            "/start - Start the bot\n"
            "/help - Help info\n"
            "/info - Bot info\n"
        )
        logging.info(f'/help from {event.sender_id}')

    @client.on(events.NewMessage)
    async def ai_chat(event):
        text = event.text.strip()
        if text.startswith('/'):
            return

        response = ai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": text}],
            max_tokens=128
        )

        answer = response.choices[0].message.content
        await event.respond(answer)
        logging.info(f"AI reply sent to {event.sender_id}")

    await client.run_until_disconnected()

asyncio.run(main())