from aiogram.filters import Command, CommandStart
from aiogram import F
from states.states import GameProgress, default_state, StateFilter, FSMContext, State
from aiogram import Router
from aiogram.types import Message, CallbackQuery
from lexicon.lexicon import lexicon
from keyboards.inline_keyboard import start_keyboard, mode_selection_keyboard, game_field, rules_keyboard
from filters.core_filters import FilterCellsCBData
from service.core_service import check_winner

GameProgress = GameProgress()

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
    await state.set_state(GameProgress.game_start)

    new_state = next(GameProgress.game_cycle)
    await state.set_state(new_state)
    await state.set_data({'now': new_state.state.strip("@:"), 'winner': None})

    data = await state.get_data()
    await cb.message.edit_text(text=f'Игра началась! Сейчас ходит - {data["now"]}', reply_markup=game_field)


@router.callback_query(FilterCellsCBData)
async def game_process(cb: CallbackQuery, state: FSMContext):
    x, y = eval(cb.data)
    data = await state.get_data()
    print(data)
    if data['winner'] is None:
        if cb.message.reply_markup.inline_keyboard[x][y].text == '◻️':

            cb.message.reply_markup.inline_keyboard[x][y].text = data['now'] == 'Крестик' and '✕' or 'O'

            next_now = next(GameProgress.game_cycle)
            await state.update_data({'now': next_now.state.strip('@:')})
            await cb.message.edit_text(
                text=f'{data["now"]} сделал свой ход! Теперь ходит {next_now.state.strip("@:")}!',
                reply_markup=cb.message.reply_markup)
            await state.update_data({"winner": check_winner(cb)})
        else:
            await cb.answer('Нельзя пойти на эту клетку!')
    else:
        winner = data['winner']
        if winner in '✕O':
            winner = winner == '✕' and 'Крестик' or 'Нолик'
            await cb.message.edit_text(text=f'Игра закончена! Победил {winner}!')
        else:
            await cb.message.edit_text(text=f'Игра закончена! {winner}!')
