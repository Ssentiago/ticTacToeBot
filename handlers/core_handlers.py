import pprint

from aiogram.filters import CommandStart, Command
from aiogram import F
from states.states import Game, StateFilter, FSMContext
from aiogram import Router
from aiogram.types import Message, CallbackQuery
from lexicon.lexicon import lexicon
from keyboards.inline_keyboard import TTTKeyboard
from filters.core_filters import FilterCellsCBData
from service.core_service import check_winner

signs = {'✕': 'Крестик', 'O': 'Нолик'}
game_pool = {'pool': {}, 'pairs': set()}
router = Router()


@router.message(~StateFilter(Game.two_players_on_one_computer), ~StateFilter(Game.player_vs_player), CommandStart())
async def start_message(message: Message, state: FSMContext):
    await state.set_state(Game.default)
    keyboard = TTTKeyboard.create_simple_inline_keyboard(2, 'Начать', 'Правила')
    await message.answer(lexicon.start, reply_markup=keyboard)


@router.callback_query(F.data == 'Правила')
async def rules(callback: CallbackQuery):
    keyboard = TTTKeyboard.create_simple_inline_keyboard(1, 'Назад')
    await callback.message.edit_text(text=lexicon.rules, reply_markup=keyboard)


@router.callback_query(F.data == 'Назад')
async def back(callback: CallbackQuery):
    keyboard = TTTKeyboard.create_simple_inline_keyboard(2, 'Начать', 'Правила')
    await callback.message.edit_text(text=lexicon.start, reply_markup=keyboard)


@router.callback_query(F.data == 'Начать')
async def begin(cb: CallbackQuery):
    keyboard = TTTKeyboard.create_simple_inline_keyboard(1, 'Один игрок: компьютер', 'Один игрок: другой игрок', 'Два игрока')
    await cb.message.edit_text(text=lexicon.mode, reply_markup=keyboard)


@router.callback_query(F.data == 'Два игрока')
async def two_players(cb: CallbackQuery, state: FSMContext):
    await state.set_state(Game.two_players_on_one_computer)

    sign = '✕'

    await state.set_data({'winner': None, 'sign': sign})
    await cb.message.edit_text(text=f'Игра началась! Сейчас ходит - {signs[sign]}', reply_markup=TTTKeyboard.create_game_field(3))


@router.callback_query(StateFilter(Game.two_players_on_one_computer, Game.player_vs_player), FilterCellsCBData())
async def game_process(cb: CallbackQuery, state: FSMContext, coords: tuple[int, int]):
    x, y = coords
    if cb.message.reply_markup.inline_keyboard[x][y].text == '◻️':
        data = await state.get_data()
        cb.message.reply_markup.inline_keyboard[x][y].text = data['sign']

        next_sign = data['sign'] == 'O' and '✕' or 'O'

        await cb.message.edit_text(
            text=lexicon.game_process(signs[data['sign']], signs[next_sign]),
            reply_markup=cb.message.reply_markup)

        await state.update_data({'sign': next_sign})

        winner = check_winner(cb)

        if winner is not None:
            if winner in '✕O':
                winner = winner == '✕' and 'Крестик' or 'Нолик'

            keyboard = TTTKeyboard.create_simple_inline_keyboard(1, 'Вернуться')
            await cb.message.edit_text(text=f'Игра закончена! {(winner != "Ничья") * "Победил "}{winner}!',
                                       reply_markup=keyboard)

            await state.update_data({"winner": None})
            await state.set_state(Game.end_of_game)




    else:
        await cb.answer('Нельзя пойти на эту клетку!')

    return cb.message.reply_markup

@router.callback_query(F.data == 'Вернуться')
async def ending(cb: CallbackQuery, state: FSMContext):
    keyboard = TTTKeyboard.create_simple_inline_keyboard(2, 'Начать', 'Правила')
    await cb.message.edit_text(text=lexicon.start, reply_markup=keyboard)
    await state.set_state(Game.default)


@router.message(StateFilter(Game.two_players_on_one_computer, Game.player_vs_player), Command('cancel'))
async def cancel(cb: Message, state: FSMContext):
    await state.set_state(Game.default)
    keyboard = TTTKeyboard.create_simple_inline_keyboard(2, 'Начать', 'Правила')
    await cb.bot.send_message(cb.from_user.id, lexicon.cancel)
    await cb.bot.send_message(cb.from_user.id, lexicon.start, reply_markup=keyboard)


@router.callback_query(F.data == 'Один игрок: другой игрок')
async def search_for_players(cb: CallbackQuery, state: FSMContext):
    await state.set_state(Game.player_vs_player)
    await cb.message.edit_text('Идёт поиск игроков...')
    user_id = cb.from_user.id
    if game_pool['pool']:
        other_user_id = game_pool['pool'].popitem()

        await send_keyboard_both(user_id, other_user_id[0], state, other_user_id[1], cb.bot)
    else:
        game_pool['pool'].setdefault(user_id, state)


async def send_keyboard_both(id1: int, id2: int, state1: FSMContext, state2: FSMContext, bot):
    signs = {'✕', 'O'}
    keyboard = TTTKeyboard.create_game_field(3)
    sign1 = signs.pop()
    sign2 = signs.pop()

    msg1 = await bot.send_message(id1, lexicon.online(sign1), reply_markup=keyboard)
    msg2 = await bot.send_message(id2, lexicon.online(sign2), reply_markup=keyboard)

    await state1.update_data({'sign': sign1, 'msg_id': msg1.message_id, 'playing_now': '✕'})
    await state2.update_data({'sign': sign2, 'msg_id': msg2.message_id, 'playing_now': '✕'})

    game_pool['pairs'].add((id1, state1, id2, state2))

