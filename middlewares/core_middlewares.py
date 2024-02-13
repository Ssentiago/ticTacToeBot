from typing import Awaitable, Callable, Dict, Any
from states.states import Game, FSMContext
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from handlers.core_handlers import game_pool
from service.other_service import get_the_pair
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

        # если фильтр FiltrCellsCBData вернул координаты клетки
        # (а это значит то, что у пользователя сейчас активно игровое поле и он по нему сейчас кликнул)
        # то мы запускаем всю цепочку обработки.
        # если координат клетки нет, то мы просто передаем событие в хэндлер как обычно (значит, это событие нам не нужно)
        if 'coords' in data:

            # если пользователь находится сейчас в состоянии игры на одном компьютере, то дальнейшая обработка не требуется
            if state == Game.two_players_on_one_computer.state:
                return await handler(event, data)

            # проверяем, что пользователь находится в состоянии противоборства с другим пользователемы
            if state == Game.player_vs_player.state:
                # достаем id и состояния пользователей из пула
                pair: tuple[int, FSMContext, int, FSMContext] = await get_the_pair(game_pool, user_id)

                # достаем знак пользователя и сразу же подготавливаем следующий знак
                user_sign: str = user_data['sign']
                next_sign = user_sign == '✕' and 'O' or '✕'

                # если пользователь имеет право сейчас ходить, то обрабатываем его ход, если нет - шлём об этом уведомление
                if user_sign == user_data['playing_now']:
                    # достаем клавиатуру из хэндлера, обрабатывающего процесс игры
                    keyboard = await handler(event, data)

                    # обновляем информацию о знаке, который сейчас ходит
                    await user_state.update_data({'playing_now': next_sign})

                    # достаем из пар состояние другого игрока
                    other_user_ind = pair.index(user_id) == 0 and 2 or 0
                    other_user_data: FSMContext = pair[other_user_ind + 1]
                    other_user_data = await other_user_data.get_data()

                    # обновляем клавиатуру и сообщение у другого игрока
                    # id мы достали из пары, id сообщения - из состояния игрока, а клавиатуру вытащили из хэндлера
                    await event.bot.edit_message_text(lexicon.game_process(user_sign, next_sign),
                                                      pair[other_user_ind],
                                                      other_user_data['msg_id'], reply_markup=keyboard)



            else:
                await event.answer('Сейчас не ваш ход!')

        else:
            return await handler(event, data)
