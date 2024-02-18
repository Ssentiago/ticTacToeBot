from typing import Awaitable, Callable, Dict, Any
from states.states import Game, FSMContext
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from aiogram.types import CallbackQuery
from database.database import Database

db = Database()


class CheckingMoves(BaseMiddleware):
    async def __call__(self,
                       handler: Callable[TelegramObject: Dict[str, Any], Awaitable[Any]],
                       event: CallbackQuery,
                       data: Dict[str, Any]):

        # подготавливаем всё нужное нам - данные юзера, его состояние и id
        user_state: FSMContext = data['state']
        user_data = await user_state.get_data()
        state = data['raw_state']

        if 'callback_data' in data:
            # если пользователь играет сам с собой, то обрабатываем как обычно
            if state == Game.two_players_on_one_computer.state:
                return await handler(event, data)
            if state == Game.player_vs_computer.state:

                if user_data['playing_now'] == user_data['sign']:
                    await handler(event, data)
                else:
                    await event.answer()

            # проверяем, что пользователь играет против другого игрока
            if state == Game.player_vs_player.state:
                user_sign: str = user_data['sign']

                # если пользователь имеет право сейчас ходить, то отправляем его на обработку, если нет - шлём об этом уведомление
                if user_sign == user_data['playing_now']:
                    winner = user_data['winner']
                    if not winner:
                        return await handler(event, data)
                    else:
                        await event.answer('Подождите...')
                else:
                    await event.answer('Сейчас не ваш ход!')
            else:
                await event.answer()

        else:
            return await handler(event, data)


class DBMiddleware(BaseMiddleware):
    async def __call__(self,
                       handler: Callable[TelegramObject: Dict[str, Any], Awaitable[Any]],
                       event: CallbackQuery,
                       data: Dict[str, Any]):
        if event.data == 'Игра против другого игрока':
            await db.initiate_user(event.from_user.id, event.from_user.full_name)

        await handler(event, data)
