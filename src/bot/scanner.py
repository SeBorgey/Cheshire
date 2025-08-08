import asyncio
import logging
import time

from aiogram import Bot

import config
from src.llm.client import LLMClient
from src.memory.history_manager import HistoryManager


class ProactiveScanner:
    def __init__(
        self,
        bot: Bot,
        history_manager: HistoryManager,
        llm_client: LLMClient,
        llm_lock: asyncio.Lock,
        bot_state: dict,
    ):
        self.bot = bot
        self.history_manager = history_manager
        self.llm_client = llm_client
        self.llm_lock = llm_lock
        self.bot_state = bot_state

    async def start(self):
        logging.info("Proactive scanner started.")
        while True:
            await asyncio.sleep(5)
            try:
                await self.scan_and_act()
            except Exception as e:
                logging.error(f"Error in scanner loop: {e}", exc_info=True)

    async def scan_and_act(self):
        async with self.llm_lock:
            current_time = time.time()
            
            last_message = self.history_manager.get_last_message()
            if not last_message:
                return

            last_message_id = last_message["message_id"]
            if last_message_id <= self.bot_state.get("last_llm_trigger_message_id", 0):
                return
                
            if last_message["user_id"] == self.bot.id:
                return

            if current_time - self.bot_state.get("last_llm_call_timestamp", 0) <= config.GLOBAL_LLM_COOLDOWN_SECONDS:
                return
            
            if current_time - self.bot_state.get("last_proactive_analysis_timestamp", 0) <= config.PROACTIVE_COOLDOWN_SECONDS:
                return

            logging.info(f"Scanner triggered by message {last_message_id}. Committing to API call.")
            
            self.bot_state["last_llm_call_timestamp"] = current_time
            self.bot_state["last_proactive_analysis_timestamp"] = current_time
            self.bot_state["last_llm_trigger_message_id"] = last_message_id
            
            context = self.history_manager.get_formatted_history()
            should_respond, response_text = await self.llm_client.decide_on_proactive_response(context)

            if should_respond and response_text:
                logging.info(f"Scanner: LLM decided to respond.")
                bot_response_message = await self.bot.send_message(
                    chat_id=config.TARGET_CHAT_ID,
                    text=response_text,
                    reply_to_message_id=last_message_id,
                )
                self.history_manager.add_message(bot_response_message)
                self.history_manager.save_state()
            else:
                logging.info(f"Scanner: LLM decided not to respond. Cooldowns are active.")
