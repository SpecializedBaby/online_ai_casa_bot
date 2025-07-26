import os
from dataclasses import dataclass
from dotenv import load_dotenv


load_dotenv()


@dataclass
class Config:
    bot_token: str = None
    crypto_pay_token: str = None
    admin_ids: list = None
    db_path: str = "database.db"
    network_api_crypto_pay: str = None
    supports: list = None


def get_config() -> Config:
    return Config(
        bot_token=os.getenv("BOT_TOKEN"),
        crypto_pay_token=os.getenv("CRYPTO_PAY_TOKEN"),
        admin_ids=os.getenv("ADMIN_IDS").split(),
        db_path=os.getenv("DB_PATH"),
        network_api_crypto_pay=os.getenv("NETWORK_CRYPTO_API"),
        supports=os.getenv("SUPPORTS").split()
    )
