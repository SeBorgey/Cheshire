import asyncio
import logging

from aiogram import Bot, Dispatcher

import config
from src.bot import handlers
from src.llm.client import LLMClient
from src.memory.history_manager import HistoryManager
from src.utils.logging_setup import setup_logging


async def main():
    setup_logging()

    history_manager = HistoryManager(
        max_size=config.HISTORY_MAX_MESSAGES,
        user_map=config.USER_ID_TO_NAME_MAP,
        state_file="state.json",
    )
    history_manager.load_state()

    llm_client = LLMClient()
    llm_lock = asyncio.Lock()
    proactive_state = {"last_analysis_timestamp": 0}

    bot = Bot(token=config.BOT_TOKEN)
    bot_info = await bot.get_me()
    bot_username = bot_info.username

    dp = Dispatcher()
    dp.include_router(handlers.router)
    
    logging.info(f"Starting bot @{bot_username}...")
    
    await dp.start_polling(
        bot,
        history_manager=history_manager,
        llm_client=llm_client,
        llm_lock=llm_lock,
        proactive_state=proactive_state,
        bot_username=bot_username,
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped.")