from aiogram.types import CallbackQuery

async def get_the_pair(pool: dict, id):
    print(pool)
    for pair in pool['pairs']:
        if id in pair:
            return pair

