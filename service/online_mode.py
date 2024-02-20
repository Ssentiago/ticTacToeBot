# инициация пользователей в онлайн-режиме
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from database.database import Database
from keyboards.inline_keyboard import TTTKeyboard
from lexicon.lexicon import lexicon
from service.service import Service
from states.states import Game

db = Database()

async def initiation_of_both_users(id1: int,
                                   id2: int,
                                   state1: FSMContext,
                                   state2: FSMContext, bot):
    signs = {'✕', 'O'}
    keyboard = TTTKeyboard.create_game_field(3)
    sign1 = signs.pop()
    sign2 = signs.pop()

    msg1 = await bot.send_message(id1, lexicon.game_start(Service.signs[sign1]), reply_markup = keyboard)
    msg2 = await bot.send_message(id2, lexicon.game_start(Service.signs[sign2]), reply_markup = keyboard)

    await state1.update_data({'sign': sign1, 'msg_id': msg1.message_id, 'playing_now': '✕', 'winner': None})
    await state2.update_data({'sign': sign2, 'msg_id': msg2.message_id, 'playing_now': '✕', 'winner': None})

    Service.game_pool['pairs'].add((id1, state1, id2, state2))


# вытаскиваем данные о другом пользователе из пары и из его состояния
async def get_other_user_data(pair: tuple[int, FSMContext, int, FSMContext], user_id) -> tuple[int, int, FSMContext]:
    other_user_ind = pair.index(user_id) == 0 and 2 or 0
    other_user_id = pair[other_user_ind]
    other_user_state: FSMContext = pair[other_user_ind + 1]
    other_user_data = await other_user_state.get_data()
    msg_id = other_user_data['msg_id']
    return other_user_id, msg_id, other_user_state


async def get_the_pair(pool: dict, id: int):
    for pair in pool['pairs']:
        if id in pair:
            return pair


# получение данных о рейтинге пользователей
async def rating(cb: CallbackQuery, state: FSMContext) -> None:
    user_id = cb.from_user.id
    raw_data = await db.get_values(cb.from_user.id)
    user_rate, all = raw_data['user_data'], raw_data['all']
    return lexicon.rating(user_rate, all)


# удаление пользователей из поиска в том случае если они вышли из него при помощи /cancel
async def remove_user_from_search(id: int, state: FSMContext) -> None:
    raw_state = await state.get_state()
    x = Service.game_pool['pool'].pop(id, None)
    print(x)
    if raw_state == Game.player_vs_player:
        pair = await get_the_pair(Service.game_pool, id)
        Service.game_pool['pairs'].discard(pair)
