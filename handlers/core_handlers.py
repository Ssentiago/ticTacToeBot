from aiogram.filters import CommandStart, Command
from aiogram import F
from states.states import GameProgress, StateFilter, FSMContext
from aiogram import Router
from aiogram.types import Message, CallbackQuery
from lexicon.lexicon import lexicon
from keyboards.inline_keyboard import TTTKeyboard
from filters.core_filters import FilterCellsCBData
from service.core_service import check_winner

signs = {'✕': 'Крестик', 'O': 'Нолик'}
game_pool = {'pool': set(), 'pairs': set(), 'signs': {}}
router = Router()


@router.message(~StateFilter(GameProgress.game_cycle), ~StateFilter(GameProgress.online), CommandStart())
async def start_message(message: Message, state: FSMContext):
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
    await state.set_state(GameProgress.game_cycle)

    sign = '✕'

    await state.set_data({cb.from_user.id: {'winner': None, 'sign': sign}})
    data = await state.get_data()
    await cb.message.edit_text(text=f'Игра началась! Сейчас ходит - {signs[sign]}', reply_markup=create_game_field(3))


@router.callback_query(StateFilter(GameProgress.game_cycle), FilterCellsCBData())
async def game_process(cb: CallbackQuery, state: FSMContext, coords: tuple[int, int]):
    x, y = coords
    if cb.message.reply_markup.inline_keyboard[x][y].text == '◻️':
        data = await state.get_data()
        cb.message.reply_markup.inline_keyboard[x][y].text = data[str(cb.from_user.id)]['sign']

        next_sign = data[str(cb.from_user.id)]['sign'] == 'O' and '✕' or 'O'

        await cb.message.edit_text(
            text=lexicon.game_process(signs[data[str(cb.from_user.id)]['sign']], signs[next_sign]),
            reply_markup=cb.message.reply_markup)

        await state.update_data({str(cb.from_user.id): {'sign': next_sign}})

        winner = check_winner(cb)

        if winner is not None:
            if winner in '✕O':
                winner = winner == '✕' and 'Крестик' or 'Нолик'
            keyboard = TTTKeyboard.create_simple_inline_keyboard(1, 'Вернуться')
            await cb.message.edit_text(text=f'Игра закончена! {(winner != "Ничья") * "Победил "}{winner}!',
                                       reply_markup=keyboard)
            await state.update_data({cb.from_user.id: {"winner": None}})
            await state.set_state(GameProgress.game_end)



    else:
        await cb.answer('Нельзя пойти на эту клетку!')


@router.callback_query(F.data == 'Вернуться')
async def ending(cb: CallbackQuery, state: FSMContext):
    keyboard = TTTKeyboard.create_simple_inline_keyboard(2, 'Начать', 'Правила')
    await cb.message.edit_text(text=lexicon.start, reply_markup=keyboard)
    await state.set_state(GameProgress.default)


@router.message(StateFilter(GameProgress.game_cycle, GameProgress.online), Command('cancel'))
async def cancel(cb: Message, state: FSMContext):
    await state.set_state(GameProgress.default)
    keyboard = TTTKeyboard.create_simple_inline_keyboard(2, 'Начать', 'Правила')
    await cb.bot.send_message(cb.from_user.id, lexicon.cancel)
    await cb.bot.send_message(cb.from_user.id, lexicon.start, reply_markup=keyboard)


@router.callback_query(F.data == 'Один игрок: другой игрок')
async def search_for_players(cb: CallbackQuery, state: FSMContext):
    await state.set_state(GameProgress.online)
    await cb.message.edit_text('Идёт поиск игроков...')
    user_id = cb.from_user.id
    if game_pool['pool']:
        other_user_id = game_pool['pool'].pop()
        game_pool['pairs'].add((user_id, other_user_id))
        await send_keyboard_both(user_id, other_user_id, cb.bot)
    else:
        game_pool['pool'].add(user_id)


async def send_keyboard_both(id1, id2, bot):
    signs = {'Крестик', 'Нолик'}
    keyboard = TTTKeyboard.CREATE_GAME_FIELD(3)
    await bot.send_message(id1, lexicon.mult_user(signs.pop()), reply_markup=keyboard)
    await bot.send_message(id2, lexicon.mult_user(signs.pop()), reply_markup=keyboard)
