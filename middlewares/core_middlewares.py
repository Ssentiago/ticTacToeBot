from typing import Awaitable, Callable, Dict, Any
from states.states import Game, FSMContext
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from handlers.core_handlers import Service
from service.core_service import get_other_user_data, get_the_pair
from aiogram.types import CallbackQuery
from lexicon.lexicon import lexicon


class SomeMiddleWare(BaseMiddleware):
    async def __call__(self,
                       handler: Callable[TelegramObject: Dict[str, Any], Awaitable[Any]],
                       event: CallbackQuery,
                       data: Dict[str, Any]):

        # подготавливаем всё нужное нам - данные юзера, его состояние и id
        user_state: FSMContext = data['state']
        user_data = await user_state.get_data()
        user_id = event.from_user.id
        state = data['raw_state']

        if 'callback_data' in data:

            # если пользователь находится сейчас в состоянии игры на одном компьютере, то дальнейшая обработка не требуется
            if state == Game.two_players_on_one_computer.state:
                return await handler(event, data)

            # проверяем, что пользователь находится в состоянии противоборства с другим пользователем
            if state == Game.player_vs_player.state:
                # достаем id и состояния пользователей из пула
                pair: tuple[int, FSMContext, int, FSMContext] = await get_the_pair(Service.game_pool, user_id)

                # достаем знак пользователя и сразу же подготавливаем следующий знак
                user_sign: str = user_data['sign']
                next_sign = user_sign == '✕' and 'O' or '✕'


                # если пользователь имеет право сейчас ходить, то обрабатываем его ход, если нет - шлём об этом уведомление
                if user_sign == user_data['playing_now']:
                    return await handler(event, data)
                else:
                    await event.answer('Сейчас не ваш ход!')

        else:
            return await handler(event, data)
