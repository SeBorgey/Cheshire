import asyncio
import logging

from aiogram import Bot, Dispatcher

import config
from src.bot import handlers
from src.utils.logging_setup import setup_logging


async def main():
    setup_logging()
    
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(handlers.router)

    logging.info("Starting bot...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped.")