import os
from urllib.parse import quote

from faststream.rabbit import RabbitBroker
from pydantic_settings import BaseSettings, SettingsConfigDict
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from loguru import logger


class Config(BaseSettings):
    BOT_TOKEN: str
    CRYPTO_PAY_TOKEN: str
    ADMIN_IDS: list[int]
    DB_URL: str
    STORE_URL: str = 'sqlite:///./jobs.sqlite'
    NETWORK_CRYPTO_API: str
    SUPPORTS: list

    BASE_URL: str
    RABBITMQ_USERNAME: str
    RABBITMQ_PASSWORD: str
    RABBITMQ_HOST: str
    RABBITMQ_PORT: int
    VHOST: str

    FORMAT_LOG: str = "{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}"
    LOG_ROTATION: str = "10 MB"

    @property
    def rabbitmq_url(self) -> str:
        return (
            f"amqp://{self.RABBITMQ_USERNAME}:{quote(self.RABBITMQ_PASSWORD)}@"
            f"{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}/{self.VHOST}"
        )

    @property
    def hook_url(self) -> str:
        """Returns the webhook URL"""
        return f"{self.BASE_URL}/webhook"

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
    )


# Initialization of the configuration
config = Config()

# Logging setting
log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "log.txt")
logger.add(log_file_path, format=config.FORMAT_LOG, level="INFO", rotation=config.LOG_ROTATION)

# Creating a RabbitMQ message broker
broker = RabbitBroker(url=config.rabbitmq_url)

# Creating a planner of tasks
scheduler = AsyncIOScheduler(jobstores={"default": SQLAlchemyJobStore(url=config.STORE_URL)})
