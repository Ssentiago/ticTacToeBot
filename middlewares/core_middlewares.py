from typing import Awaitable, Callable, Dict, Any
from states.states import GameProgress, FSMContext

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from handlers.core_handlers import game_pool
from service.other_service import get_the_pair
from aiogram.types import CallbackQuery
from pprint import pprint
from lexicon.lexicon import lexicon


class SomeMiddleWare(BaseMiddleware):
    async def __call__(self,
                       handler: Callable[TelegramObject: Dict[str, Any], Awaitable[Any]],
                       event: CallbackQuery,
                       data: Dict[str, Any]):
        user_state: FSMContext = data['state']
        user_data = await user_state.get_data()
        print('inner middlware')
        game_cycle_state = GameProgress.game_cycle.state

        if 'coords' in data:
            state = data['raw_state']
            user_id = event.from_user.id
            # print(user_id)
            # print(game_pool)
            if state == GameProgress.game_cycle.state:
                return await handler(event, data)

            if state == GameProgress.online.state:
                pair = await get_the_pair(game_pool, user_id)

                user_sign = user_data['sign']

                if user_sign == user_data['playing_now']:
                    await user_state.update_data({'playing_now': user_sign == '✕' and 'O' or '✕'})
                    res = await handler(event, data)
                    if res:
                        other_user_id = pair.index(user_id) == 0 and 2 or 0
                        other_user_data: FSMContext = pair[other_user_id + 1]
                        other_user_data = await other_user_data.get_data()
                        other_user_msg = other_user_data['msg_id']
                        next_sign = user_sign == '✕' and 'O' or '✕'
                        print(other_user_data['msg_id'])
                        print(res)
                        await event.bot.edit_message_text(lexicon.game_process(user_sign, next_sign),
                                                          pair[other_user_id],
                                                          other_user_data['msg_id'], reply_markup=res)

                    return res


                else:
                    await event.answer('Сейчас не ваш ход!')
        else:
            return await handler(event, data)
