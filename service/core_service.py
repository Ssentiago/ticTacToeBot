from aiogram.types import CallbackQuery
from handlers.core_handlers import FSMContext, TTTKeyboard
from handlers.core_handlers import lexicon
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from lexicon.lexicon import lexicon
from random import choice


async def get_lines(cb: CallbackQuery | InlineKeyboardMarkup):
    if isinstance(cb, InlineKeyboardMarkup):
        kb = [list(map(lambda x: x.text, row)) for row in cb.inline_keyboard]
    else:
        kb = [list(map(lambda x: x.text, row)) for row in cb.message.reply_markup.inline_keyboard]
    hor = [x for x in kb]
    vert = [x for x in [list(i) for i in zip(*kb)]]
    d1 = [kb[i][i] for i in range(3)]
    d2 = [kb[2 - i][i] for i in range(2, -1, -1)]
    diag = [d1, d2]
    res = []
    res.extend(hor)
    res.extend(vert)
    res.extend(diag)
    return res


async def check_winner(cb: CallbackQuery, winner=None):
    lines = await get_lines(cb)
    winner = winner is None and any(x.count('✕') == 3 for x in lines) and '✕' or winner
    winner = winner is None and any(x.count('O') == 3 for x in lines) and 'O' or winner
    winner = winner is None and all(x.count('◻️') == 0 for x in lines) and 'Ничья' or winner
    return winner


async def initiate_both_users(id1: int,
                              id2: int,
                              state1: FSMContext,
                              state2: FSMContext, bot):
    signs = {'✕', 'O'}
    keyboard = TTTKeyboard.create_game_field(3)
    sign1 = signs.pop()
    sign2 = signs.pop()

    msg1 = await bot.send_message(id1, lexicon.game_start(Service.signs[sign1]), reply_markup=keyboard)
    msg2 = await bot.send_message(id2, lexicon.game_start(Service.signs[sign2]), reply_markup=keyboard)

    await state1.update_data({'sign': sign1, 'msg_id': msg1.message_id, 'playing_now': '✕', 'winner': None})
    await state2.update_data({'sign': sign2, 'msg_id': msg2.message_id, 'playing_now': '✕', 'winner': None})

    Service.game_pool['pairs'].add((id1, state1, id2, state2))


class Service:
    signs = {'✕': 'Крестик', 'O': 'Нолик'}
    game_pool = {'pool': {}, 'pairs': set()}


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


async def update_field_and_users_data(sign: str,
                                      x: int,
                                      y: int,
                                      field: InlineKeyboardMarkup,
                                      user_cb: CallbackQuery,
                                      user_state: FSMContext,
                                      user_id: int,
                                      ):
    raw_user_state = await user_state.get_state()
    next_sign = sign == '✕' and 'O' or '✕'
    field.inline_keyboard[x][y].text = sign
    text = lexicon.game_process(Service.signs[sign], Service.signs[next_sign])
    await user_cb.message.edit_text(text=text,
                                    reply_markup=field)

    if raw_user_state == Game.two_players_on_one_computer:
        await user_state.update_data(sign=next_sign)

    if raw_user_state == Game.player_vs_player.state:
        pair = await get_the_pair(Service.game_pool, user_id)
        other_user_id, msg_id, other_user_state = await get_other_user_data(pair, user_id)
        await user_cb.bot.edit_message_text(text=text,
                                            chat_id=other_user_id,
                                            message_id=msg_id,
                                            reply_markup=field)
        await user_state.update_data(playing_now=next_sign)
        await other_user_state.update_data(playing_now=next_sign)

    if raw_user_state == Game.player_vs_computer.state:
        x, y = computer_move(user_cb, user_state)
        user_data = user_state.get_data()
        comp_sign = user_data['computer_sign']
        next_sign = comp_sign == '✕' and 'O' or '✕'
        user_cb.message.reply_markup.inline_keyboard[x][y] = comp_sign
        await user_cb.message.edit_text(text=lexicon.game_process(comp_sign, next_sign))


async def ending_update(user_cb: CallbackQuery,
                        user_id: int,
                        user_state: FSMContext,
                        text: str,
                        keyboard: InlineKeyboardMarkup):
    raw_state = await user_state.get_state()
    await user_cb.message.edit_text(text=text,
                                    reply_markup=keyboard)
    await user_state.set_state(Game.end_of_game)

    if raw_state == Game.player_vs_player.state:
        pair = await get_the_pair(Service.game_pool, user_id)
        other_user_id, msg_id, other_user_state = await get_other_user_data(pair, user_id)
        await user_cb.bot.edit_message_text(text=text,
                                            chat_id=other_user_id,
                                            message_id=msg_id,
                                            reply_markup=keyboard)
        await other_user_state.set_state(Game.end_of_game)


async def computer_move(cb: CallbackQuery | list[list[str]],
                        state: FSMContext) -> tuple[int, int]:
    lines: list[list] = await get_lines(cb)
    user_data = await state.get_data()
    user_sign = user_data['sign']
    comp_sign = user_data['computer_sign']

    for ind, row in enumerate(lines):
        if user_sign in row and row.count(user_sign) < 3:
            x = ind
            print('x')
            for ind, elem in enumerate(row):
                if elem != user_sign:
                    y = ind
                    return x, y
    for ind, row in enumerate(lines):
        for ind1, row1 in enumerate(row):
            if lines[ind][ind1] == '◻️':
                return ind, ind1


async def computer_make_move(cb: CallbackQuery, state: FSMContext) -> None:
    x, y = await computer_move(cb, state)
    user_data = state.get_data()
    comp_sign = user_data['computer_sign']
    next_sign = user_data['sign']
    await state.update_data(playing_now=next_sign)
    cb.message.reply_markup.inline_keyboard[x][y] = comp_sign
    await cb.message.edit_text(text=lexicon.game_process(Service.signs[comp_sign], Service.signs[next_sign]),
                               reply_markup=cb.message.reply_markup)


