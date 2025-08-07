import logging
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
            logging.error(f"Error while communicating with LLM API: {e}")
            return None