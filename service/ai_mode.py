import asyncio
from random import random

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from lexicon.lexicon import lexicon
from service.game_logic import get_winner_lines
from service.service import Cell, Service


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
