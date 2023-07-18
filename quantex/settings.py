import enum
import typing
from pathlib import Path
from tempfile import gettempdir

from pydantic_settings import BaseSettings
from yarl import URL

TEMP_DIR = Path(gettempdir())


class LogLevel(str, enum.Enum):
    """Possible log levels."""

    NOTSET = "NOTSET"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    FATAL = "FATAL"


class Settings(BaseSettings):  # type: ignore
    """
    Application settings.

    These parameters can be configured
    with environment variables.
    """

    host: str = "127.0.0.1"
    port: int = 8000
    # quantity of workers for uvicorn
    workers_count: int = 1
    # Enable uvicorn reloading
    reload: bool = False

    # Current environment
    environment: str = "dev"

    log_level: LogLevel = LogLevel.INFO

    # Variables for the database
    db_host: str = "quantex-db"
    db_port: int = 5432
    db_user: str = "quantex"
    db_pass: str = "quantex"
    db_base: str = "quantex"
    db_echo: bool = False

    secret_key: str = "secret"

    # These values are only to prevent bug with pydantic-settings IGNORE

    investment_horizon: typing.Literal["short", "long"] = "short"
    interval: int = 30
    dsn: str = "postgresql://quantex:quantex@quantex-db:5432/quantex"
    newsfilter_user: str = "quantex"
    newsfilter_password: str = "quantex"
    edenai_api_key: str = "API_KEY"
    telegram_bot_api_key: str = "API_KEY"
    telegram_chat_id: str = "CHAT_ID"

    @property
    def db_url(self) -> URL:
        """
        Assemble database URL from settings.

        :return: database URL.
        """
        return URL.build(
            scheme="postgresql+asyncpg",
            host=self.db_host,
            port=self.db_port,
            user=self.db_user,
            password=self.db_pass,
            path=f"/{self.db_base}",
        )

    class Config:
        env_file = ".env"
        env_prefix = "QUANTEX_"
        env_file_encoding = "utf-8"


settings = Settings()
