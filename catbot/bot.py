import functools
import logging
from pathlib import Path
import re

from pydub import AudioSegment
from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import (
    filters,
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    InlineQueryHandler,
    MessageHandler,
)

from .ai import Catifier


class CatBot:
    """
    Telegram chatbot talking like a cat using ChatGPT
    """
    def __init__(self, config: dict, catifier: Catifier):
        """

        :param config: dict containing key value pairs of configuration variables
        :param catifier: ChatGPT helper class
        """
        self.config = config
        self.catifier = catifier

    def run(self):
        """
        Runs the bot until interrupted by the user
        """
        app = ApplicationBuilder().token(self.config["BOT_TOKEN"]).build()

        app.add_handler(CommandHandler("start", self.start))
        app.add_handler(InlineQueryHandler(self.inline_query))
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), self.reply))
        app.add_handler(CommandHandler("catify", self.catify))
        app.add_handler(CommandHandler("image", self.generate_image))
        app.add_handler(
            MessageHandler(filters.VOICE | filters.AUDIO, self.voice_handler)
        )
        app.add_handler(CommandHandler("help", self.help))

        app.run_polling()

    @staticmethod
    def check_authorized_user(func):

        """
        Decorator for chatbot functions to add a check for user authorization
        """
        @functools.wraps(func)
        async def inner(self, *args, **kwargs):
            update = args[0]
            user_name = update.message.from_user.username
            logging.info(f"Authorized access from user: {user_name})")
            return await func(self, *args, **kwargs)

        return inner

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Show helpful information on the options that this bot provides
        :param update: object representing an incoming update (e.g. a new message or an edited message)
        :param context:
        :return:
        """
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text="Help me!"
        )

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Start the conversation
        :param update: object representing an incoming update (e.g. a new message or an edited message)
        :param context:
        :return:
        """
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Hello there, I'm a cool cat AI assistant, here to help you out! I'm not lion when I say that"
                 " I'm ready to pounce on any task you may have for me!"
         )

    @check_authorized_user
    async def reply(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Command to reply to what the user was saying, in cat style
        :param update: object representing an incoming update (e.g. a new message or an edited message)
        :param context:
        :return:
        """
        message_text = update.message.text

        # Check if the bot's username is mentioned in the message
        if not re.search(r"@(?:CatGPT|Jinxthecatbot)\b", message_text, re.IGNORECASE):
            return  # Exit early if the bot's username is not mentioned

        response = await self.catifier.reply(message_text)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response)

    @check_authorized_user
    async def catify(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Command to send back the incoming message, but in cat style
        :param update: object representing an incoming update (e.g. a new message or an edited message)
        :param context:
        :return:
        """
        message_text = update.message.text
        response = await self.catifier.catify(message_text)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response)

    @check_authorized_user
    async def voice_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Command to handle an incoming voice message or audio file
        :param update: object representing an incoming update (e.g. a new message or an edited message)
        :param context:
        :return:
        """
        file_id = update.message.voice.file_id
        file_ogg = f"{file_id}.ogg"
        file_mp3 = f"{file_id}.mp3"
        file = await context.bot.get_file(file_id)
        await file.download_to_drive(file_ogg)

        AudioSegment.from_ogg(file_ogg).export(file_mp3, format="mp3")
        audio_file = open(file_mp3, "rb")

        message = await self.catifier.transcribe(audio_file)
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=message
        )
        # clean up audio files
        Path(file_ogg).unlink(missing_ok=True)
        Path(file_mp3).unlink(missing_ok=True)

    async def inline_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handles an inline query. This is when you type @botusername <query>
        :param update:
        :param context:
        :return:
        """
        query = update.inline_query.query
        if not query:
            return

        results = [
            InlineQueryResultArticle(
                id=query,
                title="Ask CatGPT",
                input_message_content=InputTextMessageContent(query),
                description=query,
                thumb_url='https://user-images.githubusercontent.com/13839523/227260331-764d699a-e99f-4920-9b03-6b2bae6e0fda.png'
            )
        ]
        await update.inline_query.answer(results)

    async def generate_image(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Interface to the DALL E image generation. Not particularly cat-specific though.
        :param update:
        :param context:
        :return:
        """
        IMAGE_SIZE = "512x512"
        prompt = update.message.text
        image_url = await self.catifier.generate_image(prompt, IMAGE_SIZE)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Look at this image: {image_url}"
        )
