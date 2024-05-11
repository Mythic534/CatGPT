import asyncio
import logging

from dotenv import dotenv_values
from catbot import CatBot, Catifier

# Setup logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


if __name__ == "__main__":
    config = dotenv_values()
    ai = Catifier(config)
    bot = CatBot(config, ai)
    bot.run()
