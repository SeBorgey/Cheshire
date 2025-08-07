import asyncio
import logging
import time

from aiogram import F, Bot, Router, types
from aiogram.filters import Command

import config
from src.llm.client import LLMClient
from src.memory.history_manager import HistoryManager

router = Router()

@router.message(Command("ping"))
async def ping_handler(message: types.Message):
    await message.answer("pong")


@router.message(F.chat.id == config.TARGET_CHAT_ID)
async def message_handler(
    message: types.Message,
    bot: Bot,
    history_manager: HistoryManager,
    llm_client: LLMClient,
    llm_lock: asyncio.Lock,
    proactive_state: dict,
    bot_username: str,
):
    history_manager.add_message(message)

    is_reply_to_bot = (
        message.reply_to_message and 
        message.reply_to_message.from_user.id == bot.id
    )
    is_mention = message.text and f"@{bot_username}" in message.text

    if is_reply_to_bot or is_mention:
        async with llm_lock:
            logging.info("Reactive mode triggered.")
            context = history_manager.get_formatted_history()
            response_text = await llm_client.generate_reply(context)
            if response_text:
                bot_response_message = await message.reply(response_text)
                history_manager.add_message(bot_response_message)
    else:
        current_time = time.time()
        last_analysis_time = proactive_state.get("last_analysis_timestamp", 0)
        
        if current_time - last_analysis_time > config.PROACTIVE_COOLDOWN_SECONDS:
            async with llm_lock:
                proactive_state["last_analysis_timestamp"] = current_time
                logging.info("Proactive mode triggered.")
                
                context = history_manager.get_formatted_history()
                should_respond, response_text = await llm_client.decide_on_proactive_response(context)
                
                if should_respond and response_text:
                    logging.info(f"LLM decided to respond proactively.")
                    bot_response_message = await bot.send_message(
                        chat_id=config.TARGET_CHAT_ID,
                        text=response_text
                    )
                    history_manager.add_message(bot_response_message)
                else:
                    logging.info("LLM decided not to respond.")

    history_manager.save_state()