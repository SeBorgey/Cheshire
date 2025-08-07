import asyncio
import logging

from aiogram import Bot, Dispatcher

import config
from src.bot import handlers
from src.memory.history_manager import HistoryManager
from src.utils.logging_setup import setup_logging


async def main():
    setup_logging()

    history_manager = HistoryManager(
        max_size=config.HISTORY_MAX_MESSAGES,
        user_map=config.USER_ID_TO_NAME_MAP,
        state_file="state.json"
    )
    history_manager.load_state()

    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(handlers.router)

    logging.info("Starting bot...")
    
    # The line `await bot.delete_webhook(drop_pending_updates=True)` is removed.
    # Now, aiogram will process all messages that the bot missed while it was offline.
    
    await dp.start_polling(bot, history_manager=history_manager)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped.")