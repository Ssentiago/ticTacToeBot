from aiogram.types import CallbackQuery
from handlers.core_handlers import FSMContext, TTTKeyboard
from handlers.core_handlers import lexicon
from aiogram.types import InlineKeyboardMarkup


def check_winner(cb: CallbackQuery, winner=None):
    check_kb = cb.message.reply_markup.inline_keyboard
    check_kb = [list(map(lambda x: x.text, row)) for row in check_kb]

    # проверка строчек.
    winner = (not winner and
              any(row == [(win := '✕')] * 3 or row == [(win := 'O')] * 3 for row in check_kb)
              and win or winner)
    # проверка столбцов
    winner = (not winner and
              any(row == [(win := '✕')] * 3 or row == [(win := 'O')] * 3 for row in (list(row) for row in zip(*check_kb)))
              and win or winner)

    # вспомогательная строчка с значениями главной диагонали
    main_d = not winner and ''.join([check_kb[i][i] for i in range(3)])
    # вспомогательная строчка с значениями побочной диагонали
    side_d = not winner and ''.join([check_kb[2 - i][i] for i in range(2, -1, -1)])

    # проверяем диагонали.
    winner = not winner and (main_d == (win := '✕') * 3 or main_d == (win := 'O') * 3
                             or side_d == (win := '✕') * 3 or side_d == (win := 'O') * 3) and win or winner
    # проверка на ничью
    winner = not winner and all(x != '◻️' for row in check_kb for x in row) and 'Ничья' or winner

    return winner


async def initiate_both_users(id1: int, id2: int, state1: FSMContext, state2: FSMContext, bot):
    signs = {'✕', 'O'}
    keyboard = TTTKeyboard.create_game_field(3)
    sign1 = signs.pop()
    sign2 = signs.pop()

    msg1 = await bot.send_message(id1, lexicon.online(Service.signs[sign1]), reply_markup=keyboard)
    msg2 = await bot.send_message(id2, lexicon.online(Service.signs[sign2]), reply_markup=keyboard)

    await state1.update_data({'sign': sign1, 'msg_id': msg1.message_id, 'playing_now': '✕', 'winner': None})
    await state2.update_data({'sign': sign2, 'msg_id': msg2.message_id, 'playing_now': '✕', 'winner': None})

    Service.game_pool['pairs'].add((id1, state1, id2, state2))


class Service:
    signs = {'✕': 'Крестик', 'O': 'Нолик'}
    game_pool = {'pool': {}, 'pairs': set()}


async def get_other_user_data(pair: tuple[int, FSMContext, int, FSMContext], user_id) -> tuple[int, FSMContext, dict]:
    other_user_ind = pair.index(user_id) == 0 and 2 or 0
    other_user_id = pair[other_user_ind]
    other_user_state: FSMContext = pair[other_user_ind + 1]
    other_user_data = await other_user_state.get_data()

    return other_user_id, other_user_state, other_user_data



