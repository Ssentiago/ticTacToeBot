import asyncio
import random

from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from handlers.core_handlers import FSMContext, TTTKeyboard, lexicon, Game
from bot import db
from service.other_service import Cell, Service

# получаем выигрышные линии - горизонтали, вертикали и диагонали для удобной с ними работы
async def get_winner_lines(cb: CallbackQuery):
    kb = [list(map(lambda x: x.text, row)) for row in cb.message.reply_markup.inline_keyboard]
    for ind, row in enumerate(kb):
        for elem_ind, elem in enumerate(row):
            kb[ind][elem_ind] = Cell(ind, elem_ind, elem)

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

# проверяем что хотя бы на одной из выигрышных линий есть символы одного из игроков
# если ни на одной линии нет пустой клетки - то ничья
async def check_winner(cb: CallbackQuery, winner = None):
    lines = [[elem.text for elem in row] for row in (await get_winner_lines(cb))]
    winner = winner is None and any(x.count('✕') == 3 for x in lines) and '✕' or winner
    winner = winner is None and any(x.count('O') == 3 for x in lines) and 'O' or winner
    winner = winner is None and all(x.count('◻️') == 0 for x in lines) and 'Ничья' or winner
    return winner

# инициация пользователей в онлайн-режиме
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


# обновляем игровое поле и данные игроков
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
    await user_cb.message.edit_text(text = text,
                                    reply_markup = field)

    if raw_user_state == Game.two_players_on_one_computer:
        await user_state.update_data(sign = next_sign)

    elif raw_user_state == Game.player_vs_computer.state:
        winner = await check_winner(user_cb)
        if winner is None:
            await user_state.update_data(playing_now = next_sign)
            await computer_make_move(user_cb, user_state)
            await user_state.update_data(playing_now = sign)

    elif raw_user_state == Game.player_vs_player.state:
        pair = await get_the_pair(Service.game_pool, user_id)
        other_user_id, msg_id, other_user_state = await get_other_user_data(pair, user_id)
        await user_cb.bot.edit_message_text(text = text,
                                            chat_id = other_user_id,
                                            message_id = msg_id,
                                            reply_markup = field)
        await user_state.update_data(playing_now = next_sign)
        await other_user_state.update_data(playing_now = next_sign)

# обновляем игровое поле и данные игроков в конце партии
async def ending_update(user_cb: CallbackQuery,
                        user_id: int,
                        user_state: FSMContext,
                        text: str,
                        keyboard: InlineKeyboardMarkup,
                        winner: int):
    raw_state = await user_state.get_state()

    await user_cb.message.edit_text(text = text,
                                    reply_markup = keyboard)
    await user_state.set_state(Game.end_of_game)

    if raw_state == Game.player_vs_player.state:
        pair = await get_the_pair(Service.game_pool, user_id)
        other_user_id, msg_id, other_user_state = await get_other_user_data(pair, user_id)
        await user_cb.bot.edit_message_text(text = text,
                                            chat_id = other_user_id,
                                            message_id = msg_id,
                                            reply_markup = keyboard)
        await other_user_state.set_state(Game.end_of_game)
        await remove_user_from_search(user_id, user_state)

        data = await user_state.get_data()
        winner = data['winner']
        user_sign = data['sign']
        if winner != 'Ничья':
            if winner == user_sign:
                await db.increment_wins(user_id)


async def get_empty_cell(line: list[Cell]) -> tuple[int, int]:
    for cell in line:
        if cell.text == '◻️':
            return cell.x, cell.y

# непосредственно логика алгоритма хода компьютера
async def computer_move(cb: CallbackQuery,
                        state: FSMContext) -> tuple[int, int]:
    lines: list[list[Cell]] = await get_winner_lines(cb)

    user_data = await state.get_data()
    user_sign = user_data['sign']
    comp_sign = user_data['computer_sign']

    computer_potential_winning_lines = list(filter(lambda line:
                                                   [x.text for x in line].count(comp_sign) == 2, lines))
    if computer_potential_winning_lines:
        line = computer_potential_winning_lines[0]
        return await get_empty_cell(line)

    user_potential_winning_lines = filter(lambda line:
                                          [x.text for x in line[1]].count(user_sign) > 0 and [x.text for x in line[1]].count('◻️') > 0,
                                          enumerate(lines))
    max_potential_line = max(user_potential_winning_lines, key = lambda x: [x.text for x in x[1]].count(user_sign), default = None)
    if max_potential_line:
        return await get_empty_cell(max_potential_line[1])

# ход компьютера
async def computer_make_move(cb: CallbackQuery, state: FSMContext) -> None:
    move = await computer_move(cb, state)
    if move:
        x, y = move
        user_data = await state.get_data()
        comp_sign = user_data['computer_sign']
        next_sign = user_data['sign']
        cb.message.reply_markup.inline_keyboard[x][y].text = comp_sign
        await asyncio.sleep(random.randint(1, 3))
        await cb.message.edit_text(text = lexicon.game_process(Service.signs[comp_sign], Service.signs[next_sign]),
                                   reply_markup = cb.message.reply_markup)
    else:
        await cb.answer()

# получение данных о рейтинге пользователей
async def rating(cb: CallbackQuery, state: FSMContext) -> None:
    user_id = cb.from_user.id
    raw_data = await db.get_values(cb.from_user.id)
    user_rate, all = raw_data['user_data'], raw_data['all']
    return lexicon.rating(user_rate, all)

# удаление пользователей из поиска в том случае если они вышли из него при помощи /cancel
async def remove_user_from_search(id: int, state: FSMContext) -> None:
    raw_state = await state.get_state()
    Service.game_pool['pool'].pop(int, None)
    if raw_state == Game.player_vs_player:
        pair = await get_the_pair(Service.game_pool, id)
        Service.game_pool['pairs'].discard(pair)
