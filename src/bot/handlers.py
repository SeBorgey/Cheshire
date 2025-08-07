import logging

from aiogram import F, Router, types
from aiogram.filters import Command

import config
from src.memory.history_manager import HistoryManager

router = Router()

@router.message(Command("ping"))
async def ping_handler(message: types.Message):
    await message.answer("pong")


@router.message(F.chat.id == config.TARGET_CHAT_ID)
async def message_handler(message: types.Message, history_manager: HistoryManager):
    logging.info(f"Received message in target chat {config.TARGET_CHAT_ID} (ID: {message.message_id})")
    history_manager.add_message(message)
    history_manager.save_state()