from dataclasses import dataclass
import os
from functools import cached_property
from dotenv import load_dotenv
from sqlalchemy.engine.url import URL

load_dotenv()


@dataclass
class StaticConfig:
    USERNAME_MAX_LENGTH: int = 255
    PASSWORD_MAX_LENGTH: int = 255

    FILE_NAME_MAX_LENGTH: int = 255


@dataclass
class DataBaseConfig:
    user = os.getenv("POSTGRES__USER")
    password = os.getenv("POSTGRES__PASSWORD")
    host = os.getenv("POSTGRES__HOST")
    port = os.getenv("POSTGRES__PORT")
    db = os.getenv("POSTGRES__DB")

    @cached_property
    def url(self) -> URL:
        return URL.create(
            drivername="postgresql+asyncpg",
            username=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.db,
        )


@dataclass
class Config:
    database = DataBaseConfig()
    static = StaticConfig()


config = Config()
