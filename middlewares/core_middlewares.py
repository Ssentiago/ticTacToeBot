from typing import Awaitable, Callable, Dict, Any
from states.states import Game, FSMContext
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from handlers.core_handlers import Service
from service.core_service import get_other_user_data
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

            # проверяем, что пользователь находится в состоянии противоборства с другим пользователем
            if state == Game.player_vs_player.state:
                # достаем id и состояния пользователей из пула
                pair: tuple[int, FSMContext, int, FSMContext] = await get_the_pair(Service.game_pool, user_id)

                # достаем знак пользователя и сразу же подготавливаем следующий знак
                user_sign: str = user_data['sign']
                next_sign = user_sign == '✕' and 'O' or '✕'

                # если пользователь имеет право сейчас ходить, то обрабатываем его ход, если нет - шлём об этом уведомление
                if user_sign == user_data['playing_now']:
                    # достаем клавиатуру и текст из хэндлера, обрабатывающего процесс игры
                    result = await handler(event, data)

                    if isinstance(result, tuple):
                        text, keyboard = result
                        other_user_id, other_user_state, other_user_data = await get_other_user_data(pair, user_id)
                        await other_user_state.set_state(Game.end_of_game)
                        await event.bot.edit_message_text(text,
                                                          other_user_id,
                                                          other_user_data['msg_id'],
                                                          reply_markup=keyboard)
                        return

                        # обновляем информацию о знаке, который сейчас ходит
                    # а также вытаскиваем данные другого пользователя
                    other_user_id, other_user_state, other_user_data = await get_other_user_data(pair, user_id)
                    await user_state.update_data({'playing_now': next_sign})
                    await other_user_state.update_data({'playing_now': next_sign})

                    # обновляем клавиатуру и сообщение у другого игрока
                    # id мы достали из пары, id сообщения - из состояния игрока, а клавиатуру вытащили из хэндлера
                    await event.bot.edit_message_text(lexicon.game_process(Service.signs[user_sign], Service.signs[next_sign]),
                                                      other_user_id,
                                                      other_user_data['msg_id'], reply_markup=result)



                else:
                    await event.answer('Сейчас не ваш ход!')

        else:
            return await handler(event, data)
