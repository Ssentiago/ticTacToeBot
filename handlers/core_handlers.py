import asyncio
import random

from aiogram.filters import CommandStart, Command
from aiogram import F, Router
from states.states import Game, StateFilter, FSMContext
from aiogram.types import Message, CallbackQuery
from lexicon.lexicon import lexicon
from keyboards.inline_keyboard import TTTKeyboard
from filters.core_filters import CellsCallbackFactory, CallbackData
from service.core_service import check_winner, initiate_both_users, Service, update_field_and_users_data, ending_update, computer_move

router = Router()


@router.message(StateFilter(Game.default), CommandStart())
async def start_message(message: Message,
                        state: FSMContext):
    await state.set_state(Game.default)
    keyboard = TTTKeyboard.create_simple_inline_keyboard(2, 'Начать', 'Правила')
    await message.answer(lexicon.start, reply_markup = keyboard)


@router.callback_query(F.data == 'Правила')
async def rules(callback: CallbackQuery):
    keyboard = TTTKeyboard.create_simple_inline_keyboard(1, 'Назад')
    await callback.message.edit_text(text = lexicon.rules, reply_markup = keyboard)


@router.callback_query(F.data == 'Назад')
async def back(callback: CallbackQuery):
    keyboard = TTTKeyboard.create_simple_inline_keyboard(2, 'Начать', 'Правила')
    await callback.message.edit_text(text = lexicon.start, reply_markup = keyboard)


@router.callback_query(F.data == 'Начать')
async def begin(cb: CallbackQuery):
    keyboard = TTTKeyboard.create_simple_inline_keyboard(1, 'Один игрок: компьютер', 'Один игрок: другой игрок', 'Два игрока')
    await cb.message.edit_text(text = lexicon.mode, reply_markup = keyboard)


@router.callback_query(F.data == 'Два игрока')
async def two_players(cb: CallbackQuery,
                      state: FSMContext):
    await state.set_state(Game.two_players_on_one_computer)

    sign = '✕'

    await state.set_data({'winner': None, 'sign': sign})

    await cb.message.edit_text(text = f'Игра началась! Сейчас ходит - {Service.signs[sign]}',
                               reply_markup = TTTKeyboard.create_game_field(3))


@router.callback_query(F.data == 'Вернуться')
async def ending(cb: CallbackQuery,
                 state: FSMContext):
    keyboard = TTTKeyboard.create_simple_inline_keyboard(2, 'Начать', 'Правила')
    await cb.message.edit_text(text = lexicon.start, reply_markup = keyboard)
    await state.set_state(Game.default)


@router.message(StateFilter(Game.two_players_on_one_computer, Game.player_vs_player, Game.player_vs_computer), Command('cancel'))
async def cancel(cb: Message,
                 state: FSMContext):
    await state.set_state(Game.default)
    keyboard = TTTKeyboard.create_simple_inline_keyboard(2, 'Начать', 'Правила')
    await cb.bot.send_message(cb.from_user.id, lexicon.cancel)
    await cb.bot.send_message(cb.from_user.id, lexicon.start, reply_markup = keyboard)


@router.callback_query(F.data == 'Один игрок: другой игрок')
async def search_for_players(cb: CallbackQuery,
                             state: FSMContext):
    await state.set_state(Game.player_vs_player)
    await cb.message.edit_text('Идёт поиск игроков...')
    user_id = cb.from_user.id
    if Service.game_pool['pool']:
        other_user_id = Service.game_pool['pool'].popitem()
        await initiate_both_users(user_id, other_user_id[0], state, other_user_id[1], cb.bot)
    else:
        Service.game_pool['pool'].setdefault(user_id, state)


@router.callback_query(F.data == 'Один игрок: компьютер')
async def computer(cb: CallbackQuery,
                   state: FSMContext):
    # signs = {'✕', 'O'}
    # comp_sign = signs.pop()
    # user_sign = signs.pop()
    comp_sign = '✕'
    user_sign = 'O'
    await state.set_state(Game.player_vs_computer)
    await state.update_data(sign = user_sign, computer_sign = comp_sign, playing_now = '✕')
    keyboard = TTTKeyboard.create_game_field(3)
    if comp_sign == '✕':
        await cb.message.edit_text(text = lexicon.game_start(Service.signs[user_sign]),
                                   reply_markup = keyboard)
        comp_move = random.randint(0, 2), random.randint(0, 2)
        x, y = comp_move
        keyboard.inline_keyboard[x][y].text = comp_sign
        await asyncio.sleep(random.randint(1, 3))
        await cb.message.edit_text(text = lexicon.game_process(Service.signs[comp_sign], Service.signs[user_sign]),
                                   reply_markup = keyboard)
    else:
        await cb.message.edit_text(text = lexicon.game_start(Service.signs[user_sign]),
                                   reply_markup = keyboard)
    await state.update_data(playing_now = 'O')


@router.callback_query(StateFilter(Game.two_players_on_one_computer, Game.player_vs_player, Game.player_vs_computer),
                       CellsCallbackFactory.filter())
async def game_process(cb: CallbackQuery,
                       state: FSMContext,
                       callback_data: CallbackData):
    x, y = callback_data.x, callback_data.y
    if cb.message.reply_markup.inline_keyboard[x][y].text == '◻️':
        data = await state.get_data()
        await update_field_and_users_data(data['sign'],
                                          x, y,
                                          cb.message.reply_markup,
                                          cb,
                                          state,
                                          cb.from_user.id)
        winner = await check_winner(cb)
        if winner is not None:
            if winner in '✕O':
                winner = Service.signs[winner]

            keyboard = TTTKeyboard.create_simple_inline_keyboard(1, 'Вернуться')
            end_text = f'Игра закончена! {(winner != "Ничья") * "Победил "}{winner}!'
            await asyncio.sleep(random.randint(1, 3))
            await ending_update(cb, cb.from_user.id, state, end_text, keyboard)




    else:
        await cb.answer('Нельзя пойти на эту клетку!')
