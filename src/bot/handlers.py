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
    bot_state: dict,
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
            logging.info(f"Handler received a high-priority message {message.message_id}. Checking cooldowns...")

            while time.time() - bot_state.get("last_llm_call_timestamp", 0) < config.GLOBAL_LLM_COOLDOWN_SECONDS:
                logging.info(f"Global cooldown is active. Waiting...")
                await asyncio.sleep(5)

            if message.message_id <= bot_state.get("last_llm_trigger_message_id", 0):
                logging.info(f"Message {message.message_id} was already processed by another task. Skipping.")
                history_manager.save_state()
                return
            
            bot_state["last_llm_call_timestamp"] = time.time()
            bot_state["last_llm_trigger_message_id"] = message.message_id
            
            logging.info(f"Handler is now processing message {message.message_id}.")
            context = history_manager.get_formatted_history()
            response_text = await llm_client.generate_reply(context)
            
            if response_text:
                bot_response_message = await message.reply(response_text)
                history_manager.add_message(bot_response_message)

    history_manager.save_state()