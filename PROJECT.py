"""
Telegram OCR + GPT Reasoning Bot
---------------------------------
This bot:
1. Accepts a photo from a user.
2. Extracts text using Google Gemini OCR.
3. Sends text to ChatGPT.
4. Returns the reasoning to the user.
"""

import tempfile
from dataclasses import dataclass

import google.generativeai as genai
from openai import OpenAI
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)


# ============================================================
# Configuration
# ============================================================

@dataclass
class BotConfig:
    telegram_token: str
    openai_key: str
    gemini_key: str
    endpoint: str = "https://models.github.ai/inference"
    gpt_model: str = "openai/gpt-4o"
    ocr_model: str = "gemini-2.0-flash"

    @staticmethod
    def from_env() -> "BotConfig":
        """Load configuration values directly (hardcoded)."""
        return BotConfig(
           telegram_token = "8527912876:AAGrldzpVxcroBuRNcnKYpbMc0vksZ3IaI8",
            openai_key = "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",
            gemini_key = "AIzaSyBiOZqnSEtBLBmj6vBZHrmMXDMIZ8IAXkg",
        )


# ============================================================
# OCR Service
# ============================================================

class OCRService:
    """Perform OCR using Google Gemini."""

    def __init__(self, api_key: str, model_name: str) -> None:
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)

    def extract_text(self, image_path: str) -> str:
        """Extract text from an image."""
        try:
            with open(image_path, "rb") as img:
                result = self.model.generate(
                    content=[{"type": "image", "mime_type": "image/jpeg", "data": img.read()}],
                    instructions="Extract ALL text from this image. Do NOT analyze, only output raw text."
                )

            if not hasattr(result, "text") or not result.text:
                raise RuntimeError("OCR returned empty or invalid text.")

            return result.text

        except Exception as exc:
            raise RuntimeError(f"OCR failed: {exc}") from exc


# ============================================================
# GPT Service
# ============================================================

class GPTService:
    """Interact with OpenAI-compatible GPT model."""

    def __init__(self, api_key: str, endpoint: str, model_name: str) -> None:
        self.client = OpenAI(api_key=api_key, base_url=endpoint)
        self.model_name = model_name

    def ask(self, text: str) -> str:
        """Send text to GPT and return the response."""
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "Analyze the following extracted text."},
                    {"role": "user", "content": text},
                ]
            )
            # Fix: access content via .message.content
            return response.choices[0].message.content

        except Exception as exc:
            raise RuntimeError(f"GPT request failed: {exc}") from exc


# ============================================================
# Telegram Bot
# ============================================================

class TelegramBot:
    """Main Telegram bot handling messages."""

    def __init__(self, config: BotConfig) -> None:
        self.config = config
        self.ocr_service = OCRService(config.gemini_key, config.ocr_model)
        self.gpt_service = GPTService(config.openai_key, config.endpoint, config.gpt_model)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(
            "Send me a photo. I will extract the text using OCR and analyze it with ChatGPT."
        )

    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        try:
            if not update.message.photo:
                await update.message.reply_text("No photo received.")
                return

            file = await update.message.photo[-1].get_file()
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                img_path = tmp.name
                await file.download_to_drive(custom_path=img_path)

            text = self.ocr_service.extract_text(img_path)

            if not text.strip():
                await update.message.reply_text("No readable text found in the image.")
                return

            # Escape MarkdownV2
            safe_text = text.replace("_", "\\_").replace("*", "\\*").replace("[", "\\[").replace("]", "\\]")
            await update.message.reply_text(f"*Extracted text:*\n{safe_text}", parse_mode="MarkdownV2")

            answer = self.gpt_service.ask(text)
            safe_answer = answer.replace("_", "\\_").replace("*", "\\*").replace("[", "\\[").replace("]", "\\]")
            await update.message.reply_text(f"*ChatGPT Answer:*\n{safe_answer}", parse_mode="MarkdownV2")

        except Exception as exc:
            await update.message.reply_text(f"Error processing your photo: {exc}")

    async def chat(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        try:
            answer = self.gpt_service.ask(update.message.text)
            await update.message.reply_text(answer)
        except Exception as exc:
            await update.message.reply_text(f"Error: {exc}")

    def run(self) -> None:
        application = Application.builder().token(self.config.telegram_token).build()
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(MessageHandler(filters.PHOTO, self.handle_photo))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.chat))
        print("Bot is running...")
        application.run_polling()


# ============================================================
# Entry Point
# ============================================================

def main() -> None:
    config = BotConfig.from_env()
    bot = TelegramBot(config)
    bot.run()


if __name__ == "__main__":
    main()
