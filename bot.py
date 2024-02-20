import asyncio
import logging

from aiogram import Bot, Dispatcher
from config.config import load_config, Config
from handlers import core_handlers
from states.states import storage
from logs import log_config
from middlewares.core_middlewares import CheckingMoves, DBMiddleware
from menu.menu import set_menu
from database.database import Database

db = Database()

async def main():
    config: Config = load_config()
    bot = Bot(config.tg_bot.token)
    dp = Dispatcher(storage=storage)
    dp.startup.register(set_menu)
    dp.include_router(core_handlers.router)
    core_handlers.router.callback_query.middleware(CheckingMoves())
    core_handlers.router.callback_query.middleware(DBMiddleware())

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
