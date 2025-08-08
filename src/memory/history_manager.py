import json
import logging
from collections import deque
from datetime import datetime
from aiogram.types import Message


class HistoryManager:
    def __init__(self, max_size: int, user_map: dict, state_file: str):
        self.user_map = user_map
        self.state_file = state_file
        self.buffer = deque(maxlen=max_size)
        self.seen_message_ids = set()

    def add_message(self, message: Message):
        if not hasattr(message, 'text') or not message.text or message.message_id in self.seen_message_ids:
            return

        self.seen_message_ids.add(message.message_id)
        
        message_data = {
            "message_id": message.message_id,
            "user_id": message.from_user.id,
            "text": message.text,
            "timestamp": message.date.timestamp()
        }
        self.buffer.append(message_data)
        
    def get_last_message(self) -> dict | None:
        return self.buffer[-1] if self.buffer else None

    def get_formatted_history(self) -> str:
        lines = []
        for msg_data in self.buffer:
            dt_object = datetime.fromtimestamp(msg_data["timestamp"])
            formatted_date = dt_object.strftime('%Y-%m-%d %H:%M:%S')
            user_id = msg_data["user_id"]
            user_name = self.user_map.get(user_id, f"User {user_id}")
            text = msg_data["text"]
            lines.append(f"[{formatted_date}] {user_name}: {text}")
        return "\n".join(lines)

    def save_state(self):
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(list(self.buffer), f, ensure_ascii=False, indent=2)
        except IOError as e:
            logging.error(f"Failed to save state to {self.state_file}: {e}")

    def load_state(self):
        try:
            with open(self.state_file, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)
                self.buffer.clear()
                self.seen_message_ids.clear()
                
                for msg_data in loaded_data:
                    self.buffer.append(msg_data)
                    self.seen_message_ids.add(msg_data["message_id"])

            logging.info(f"Loaded {len(self.buffer)} messages from {self.state_file}")
        except FileNotFoundError:
            logging.info(f"{self.state_file} not found, starting with empty history.")
        except (json.JSONDecodeError, IOError) as e:
            logging.error(f"Failed to load or parse {self.state_file}, starting fresh: {e}")
            self.buffer.clear()
            self.seen_message_ids.clear()