from environs import Env
from dataclasses import dataclass


@dataclass
class TgBot:
    token: str


@dataclass
class Config:
    tg_bot: TgBot


def load_config(path: str | None = None) -> None:
    env: Env = Env()
    env.read_env(path)

    return Config(
        tg_bot = TgBot(env('bot_token')),
    )
