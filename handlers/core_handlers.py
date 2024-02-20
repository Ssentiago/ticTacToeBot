import asyncio
import random

from aiogram.filters import CommandStart, Command
from aiogram import F, Router

from service.game_logic import check_winner
from service.online_mode import initiation_of_both_users, rating, remove_user_from_search
from service.service import Service, ending_update, update_field_and_users_data
from states.states import Game, StateFilter, FSMContext
from aiogram.types import Message, CallbackQuery
from lexicon.lexicon import lexicon
from keyboards.inline_keyboard import TTTKeyboard
from filters.core_filters import CellsCallbackFactory, CallbackData
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
    keyboard = TTTKeyboard.create_simple_inline_keyboard(1, 'Компьютер', 'Игра против другого игрока', 'На двоих')
    await cb.message.edit_text(text = lexicon.mode, reply_markup = keyboard)


@router.callback_query(F.data == 'На двоих')
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


@router.message(Command('cancel'))
async def cancel(cb: Message,
                 state: FSMContext):
    await remove_user_from_search(cb.from_user.id, state)
    await state.set_state(Game.default)
    keyboard = TTTKeyboard.create_simple_inline_keyboard(2, 'Начать', 'Правила')
    await cb.bot.send_message(cb.from_user.id, lexicon.cancel)
    await cb.bot.send_message(cb.from_user.id, lexicon.start, reply_markup = keyboard)


@router.callback_query(F.data == 'Игра против другого игрока')
async def online_menu(cb: CallbackQuery,
                      state: FSMContext):
    await cb.message.edit_text(text = lexicon.mode_rating,
                               reply_markup = TTTKeyboard.create_simple_inline_keyboard(1, 'Поиск игроков', 'Рейтинг',
                                                                                        'Назад к выбору режима'))


@router.callback_query(F.data == 'Рейтинг')
async def rating_online(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_text(text = await rating(cb, state),
                               reply_markup = TTTKeyboard.create_simple_inline_keyboard(1, 'Назад к выбору игроков'),
                               parse_mode = 'HTML')


@router.callback_query(F.data == 'Назад к выбору режима')
async def back_to_mode(cb: CallbackQuery, state: FSMContext):
    keyboard = TTTKeyboard.create_simple_inline_keyboard(1, 'Компьютер', 'Игра против другого игрока', 'На двоих')
    await cb.message.edit_text(text = lexicon.mode, reply_markup = keyboard)


@router.callback_query(F.data == 'Назад к выбору игроков')
async def some_back_rating(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_text(text = lexicon.mode_rating,
                               reply_markup = TTTKeyboard.create_simple_inline_keyboard(1, 'Поиск игроков', 'Рейтинг'))


@router.callback_query(F.data == 'Поиск игроков')
async def search_for_players(cb: CallbackQuery,
                             state: FSMContext):
    await state.set_state(Game.player_vs_player)
    await cb.message.edit_text('Идёт поиск игроков...')
    user_id = cb.from_user.id
    if Service.game_pool['pool']:
        other_user_id = Service.game_pool['pool'].popitem()
        await initiation_of_both_users(user_id, other_user_id[0], state, other_user_id[1], cb.bot)
    else:
        Service.game_pool['pool'][user_id] = state


@router.callback_query(F.data == 'Компьютер')
async def computer(cb: CallbackQuery,
                   state: FSMContext):
    # случайно распределяем знаки
    # signs = ['✕', 'O']
    # comp_sign = random.choice(signs)
    # signs.remove(comp_sign)
    # user_sign = signs.pop()
    user_sign = '✕'
    comp_sign = 'O'
    # устанавливаем пользователю статус и нужные данные
    await state.set_state(Game.player_vs_computer)
    await state.update_data(sign = user_sign, computer_sign = comp_sign, playing_now = '✕', winner = None)
    keyboard = TTTKeyboard.create_game_field(3)
    # если компьютер ходит первым
    if comp_sign == '✕':
        await cb.message.edit_text(text = lexicon.game_start(Service.signs[user_sign]),
                                   reply_markup = keyboard)
        comp_move = random.randint(0, 2), random.randint(0, 2)
        x, y = comp_move
        keyboard.inline_keyboard[x][y].text = comp_sign
        await asyncio.sleep(random.randint(1, 3))
        await cb.message.edit_text(text = lexicon.game_process(Service.signs[comp_sign], Service.signs[user_sign]),
                                   reply_markup = keyboard)
        await state.update_data(playing_now = 'O')
    else:
        # первым ходит пользователь
        await cb.message.edit_text(text = lexicon.game_start(Service.signs[user_sign]),
                                   reply_markup = keyboard)


@router.callback_query(StateFilter(Game.two_players_on_one_computer, Game.player_vs_player, Game.player_vs_computer),
                       CellsCallbackFactory.filter())
async def game_process(cb: CallbackQuery,
                       state: FSMContext,
                       callback_data: CallbackData):
    # обрабатываем только ходы пользователей
    # забираем координаты их кода
    x, y = callback_data.x, callback_data.y
    if cb.message.reply_markup.inline_keyboard[x][y].text == '◻️':
        data = await state.get_data()
        winner = data['winner']
        # если победитель всё ещё не определен
        if not winner:
            # обновляем поле
            await update_field_and_users_data(data['sign'],
                                              x, y,
                                              cb.message.reply_markup,
                                              cb,
                                              state,
                                              cb.from_user.id)
            winner = await check_winner(cb)
            await state.update_data(winner = winner)
            # если победитель вдруг определился
            if winner is not None:
                if winner in '✕O':
                    winner = Service.signs[winner]
                keyboard = TTTKeyboard.create_simple_inline_keyboard(1, 'Вернуться')
                end_text = f'Игра закончена! {(winner != "Ничья") * "Победил "}{winner}!'
                await asyncio.sleep(random.randint(1, 3))
                # обновляем данные поля итогом партии
                await ending_update(cb, cb.from_user.id, state, end_text, keyboard, cb.from_user.id)
    else:
        await cb.answer('Нельзя пойти на эту клетку!')
