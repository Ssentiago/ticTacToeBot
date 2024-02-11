from environs import Env
from dataclasses import dataclass


@dataclass
class TgBot:
    token: str
    admin_id: str


@dataclass
class DatabaseConfig:
    dbname: str
    user: str
    password: str
    host: str
    port: str


@dataclass
class Config:
    tg_bot: TgBot
    db_config: DatabaseConfig


def load_config(path: str | None = None) -> None:
    env: Env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot(env('bot_token'), env('admin_id')),
        db_config=DatabaseConfig(env('dbname'), env('user'), env('pass'), env('host'), env('port'))
    )
