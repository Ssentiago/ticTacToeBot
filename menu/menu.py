from aiogram.types import BotCommand
from aiogram import Bot


async def set_menu(bot: Bot):
    main_menu = [
        BotCommand(command='/start',
                   description='главное меню'),
        BotCommand(command='/cancel', description='Отменить текущую игру')
    ]

    await bot.set_my_commands(main_menu)
