import json
import logging
from typing import Tuple

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion

import config
from src.llm import prompts


class LLMClient:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=config.OPENAI_API_KEY,
            base_url=config.OPENROUTER_API_BASE,
        )

    async def generate_reply(self, context: str) -> str | None:
        messages = [
            {"role": "system", "content": prompts.REACTIVE_SYSTEM_PROMPT},
            {"role": "user", "content": context},
        ]
        try:
            response: ChatCompletion = await self.client.chat.completions.create(
                model=config.LLM_MODEL_NAME,
                messages=messages,
                temperature=config.LLM_TEMPERATURE,
                max_tokens=config.LLM_MAX_TOKENS,
            )
            if response.choices:
                return response.choices[0].message.content.strip()
            logging.warning("LLM response has no choices.")
            return None
        except Exception as e:
            logging.error(f"Error in generate_reply: {e}")
            return None

    async def decide_on_proactive_response(self, context: str) -> Tuple[bool, str]:
        messages = [
            {"role": "system", "content": prompts.PROACTIVE_SYSTEM_PROMPT},
            {"role": "user", "content": context},
        ]
        try:
            response: ChatCompletion = await self.client.chat.completions.create(
                model=config.LLM_MODEL_NAME,
                messages=messages,
                temperature=config.LLM_TEMPERATURE,
                max_tokens=config.LLM_MAX_TOKENS,
                response_format={"type": "json_object"},
            )

            if not response.choices:
                return False, ""
            
            response_json_str = response.choices[0].message.content
            decision_data = json.loads(response_json_str)

            should_respond = decision_data.get("should_respond", False)
            response_text = decision_data.get("response_text", "")

            if should_respond and response_text:
                return True, response_text
            
            return False, ""

        except Exception as e:
            logging.error(f"Error in decide_on_proactive_response: {e}")
            return False, ""