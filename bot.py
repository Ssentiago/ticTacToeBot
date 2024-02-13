import asyncio
import logging

from aiogram import Bot, Dispatcher
from config.config import load_config, Config
from handlers import core_handlers, other_handlers
from states.states import storage
from logs import log_config
from middlewares.core_middlewares import SomeMiddleWare


async def main():
    config: Config = load_config()
    bot = Bot(config.tg_bot.token)
    dp = Dispatcher(storage=storage)
    dp.include_router(core_handlers.router)
    dp.include_router(other_handlers.router)
    core_handlers.router.callback_query.middleware(SomeMiddleWare())

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
