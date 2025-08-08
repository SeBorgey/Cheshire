# Telegram Bot Token
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

# OpenRouter API Key and Base URL
OPENAI_API_KEY = "YOUR_OPENROUTER_KEY_HERE"
OPENROUTER_API_BASE = "https://openrouter.ai/api/v1"

# LLM Parameters
LLM_MODEL_NAME = "deepseek/deepseek-chat-v3-0324:free"
LLM_TEMPERATURE = 1
LLM_MAX_TOKENS = 4096

# Target chat ID for the bot to operate in
# Note: For groups, this ID usually starts with a "-"
TARGET_CHAT_ID = -1001234567890

# A map of user IDs to their names for better context formatting
USER_ID_TO_NAME_MAP = {
    123456789: "Алексей",
    987654321: "Мария",
    111222333: "Сергей",
}

# Cooldown in seconds for ANY LLM call to prevent rate-limiting
GLOBAL_LLM_COOLDOWN_SECONDS = 60  # 1 minute

# Cooldown in seconds for proactive analysis
PROACTIVE_COOLDOWN_SECONDS = 600  # 10 minutes

# The number of latest messages to keep in memory
HISTORY_MAX_MESSAGES = 100

# Set to True to enable proactive messages, False to only respond to replies/mentions
PROACTIVE_MODE_ENABLED = True
