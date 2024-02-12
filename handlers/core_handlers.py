from aiogram.filters import CommandStart
from aiogram import F
from states.states import GameProgress, StateFilter, FSMContext
from aiogram import Router
from aiogram.types import Message, CallbackQuery
from lexicon.lexicon import lexicon
from keyboards.inline_keyboard import game_field, create_inline_keyboard
from filters.core_filters import FilterCellsCBData
from service.core_service import check_winner

signs = {'✕': 'Крестик', 'O': 'Нолик'}
game_pool = {'pool': set()}
router = Router()


@router.message(~StateFilter(GameProgress.game_cycle), CommandStart())
async def start_message(message: Message, state: FSMContext):
    keyboard = create_inline_keyboard(2, 'Начать', 'Правила')
    await message.answer(lexicon.start, reply_markup=keyboard)


@router.callback_query(F.data == 'Правила')
async def rules(callback: CallbackQuery):
    keyboard = create_inline_keyboard(1, 'Назад')
    await callback.message.edit_text(text=lexicon.rules, reply_markup=keyboard)


@router.callback_query(F.data == 'Назад')
async def back(callback: CallbackQuery):
    keyboard = create_inline_keyboard(2, 'Начать', 'Правила')
    await callback.message.edit_text(text=lexicon.start, reply_markup=keyboard)


@router.callback_query(F.data == 'Начать')
async def begin(cb: CallbackQuery):
    keyboard = create_inline_keyboard(1, 'Один игрок: компьютер', 'Один игрок: другой игрок', 'Два игрока')
    await cb.message.edit_text(text=lexicon.mode, reply_markup=keyboard)


@router.callback_query(F.data == 'Два игрока')
async def two_players(cb: CallbackQuery, state: FSMContext):
    await state.set_state(GameProgress.game_cycle)

    sign = '✕'

    await state.set_data({'winner': None, 'sign': sign})
    await cb.message.edit_text(text=f'Игра началась! Сейчас ходит - {signs[sign]}', reply_markup=game_field)


@router.callback_query(StateFilter(GameProgress.game_cycle),FilterCellsCBData())
async def game_process(cb, state: FSMContext, coords: tuple[int, int]):
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
            keyboard = create_inline_keyboard(1, 'Вернуться')
            await cb.message.edit_text(text=f'Игра закончена! {(winner != "Ничья") * "Победил "}{winner}!',
                                       reply_markup=keyboard)
            await state.update_data({"winner": winner})
            await state.set_state(GameProgress.game_end)



    else:
        await cb.answer('Нельзя пойти на эту клетку!')


@router.callback_query(F.data == 'Вернуться')
async def ending(cb: CallbackQuery, state: FSMContext):
    keyboard = create_inline_keyboard(2, 'Начать', 'Правила')
    await cb.message.edit_text(text=lexicon.start, reply_markup=keyboard)
    await state.set_state(GameProgress.default)


@router.callback_query(F.data == 'Один игрок: другой игрок')
async def mulitplayer(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_text(text='Вы были успешно добавлены в лист ожидания!')
    game_pool['pool'].add(cb.message.from_user.id)
    await cb.message.edit_text('Идёт поиск игроков...')
    await find_users(cb.message.from_user.id)
    print('Игрок нашёлся!')


async def find_users(finder_id):
    if len(game_pool['pool']) > 1:
        game_pool['pool'].discard(finder_id)
        gamer_id = game_pool['pool'].pop()

