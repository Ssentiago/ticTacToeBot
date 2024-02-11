from aiogram.filters import Command, CommandStart
from aiogram import F
from states.states import GameProgress, default_state, StateFilter, FSMContext, State
from aiogram import Router
from aiogram.types import Message, CallbackQuery
from lexicon.lexicon import lexicon
from keyboards.inline_keyboard import start_keyboard, mode_selection_keyboard, game_field, rules_keyboard, ending_keyboard
from filters.core_filters import FilterCellsCBData
from service.core_service import check_winner
from itertools import cycle

GameProgress = GameProgress()
signs = {'✕': 'Крестик', 'O': 'Нолик'}
router = Router()


@router.message(CommandStart())
async def start_message(message: Message):
    await message.answer(lexicon.start, reply_markup=start_keyboard)


@router.callback_query(F.data == 'Правила')
async def rules(callback: CallbackQuery):
    await callback.message.edit_text(text=lexicon.rules, reply_markup=rules_keyboard)


@router.callback_query(F.data == 'Назад')
async def back(callback: CallbackQuery):
    await callback.message.edit_text(text=lexicon.start, reply_markup=start_keyboard)


@router.callback_query(F.data == 'Начать')
async def begin(cb: CallbackQuery):
    await cb.message.edit_text(text=lexicon.mode, reply_markup=mode_selection_keyboard)


@router.callback_query(F.data == 'Два игрока')
async def two_players(cb: CallbackQuery, state: FSMContext):
    await state.set_state(GameProgress.game_cycle)

    await state.set_data({'winner': None, 'sign': '✕'})

    data = await state.get_data()
    sign = data['sign']
    await cb.message.edit_text(text=f'Игра началась! Сейчас ходит - {signs[sign]}', reply_markup=game_field)


@router.callback_query(StateFilter(GameProgress.game_cycle), FilterCellsCBData())
async def game_process(cb, state: FSMContext, coords: tuple[int]):
    x, y = coords
    data = await state.get_data()
    if cb.message.reply_markup.inline_keyboard[x][y].text == '◻️':
        cb.message.reply_markup.inline_keyboard[x][y].text = data['sign']

        if data['sign'] == 'O':
            next_sign = '✕'
        else:
            next_sign = 'O'

        await cb.message.edit_text(
            text=f'{signs[data["sign"]]} сделал свой ход! Теперь ходит {signs[next_sign]}!',
            reply_markup=cb.message.reply_markup)
        await state.update_data({'sign': next_sign})

        winner = check_winner(cb)

        if not winner is None:
            if winner in '✕O':
                winner = winner == '✕' and 'Крестик' or 'Нолик'
                await cb.message.edit_text(text=f'Игра закончена! Победил {winner}!', reply_markup=ending_keyboard)
                await state.update_data({"winner": winner})
                await state.set_state(GameProgress.game_end)

            else:
                await cb.message.edit_text(text=f'Игра закончена! {winner}!', reply_markup=ending_keyboard)
                await state.update_data({"winner": winner})
                await state.set_state(GameProgress.game_end)


    else:
        await cb.answer('Нельзя пойти на эту клетку!')


@router.callback_query(F.data == 'Вернуться')
async def ending(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_text(text=lexicon.start, reply_markup=start_keyboard)
    await state.set_state(default_state)
