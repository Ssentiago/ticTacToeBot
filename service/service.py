from aiogram.types import CallbackQuery, InlineKeyboardMarkup


from bot import db
from handlers.core_handlers import FSMContext, Game, lexicon
from service.ai_mode import computer_make_move
from service.game_logic import check_winner
from service.online_mode import get_the_pair, remove_user_from_search


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


from dataclasses import dataclass


@dataclass
class Cell:
    x: int
    y: int
    text: str


class Service:
    signs = {'✕': 'Крестик', 'O': 'Нолик'}
    game_pool = {'pool': {}, 'pairs': set()}
