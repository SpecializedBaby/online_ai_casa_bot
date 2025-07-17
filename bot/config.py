import os
from dataclasses import dataclass
from dotenv import load_dotenv


load_dotenv()


@dataclass
class Config:
    bot_token: str = None


def get_config() -> Config:
    return Config(bot_token=os.getenv("BOT_TOKEN"))
