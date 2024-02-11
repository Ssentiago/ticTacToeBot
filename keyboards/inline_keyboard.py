from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

kd = [[InlineKeyboardButton(callback_data=f'({row}, {col})', text='◻️') for col in range(3)] for row in range(3)]

game_field = InlineKeyboardMarkup(inline_keyboard=kd)
start_keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Начать', callback_data='Начать'),
                                                        InlineKeyboardButton(text='Правила', callback_data='Правила')]])
mode_selection_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text='Один игрок: компьютер', callback_data='Один игрок: компьютер')],
                     [InlineKeyboardButton(text='Один игрок: другой игрок', callback_data='Один игрок: другой игрок')],
                     [InlineKeyboardButton(text='Два игрока', callback_data='Два игрока')]])
rules_keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Назад', callback_data='Назад')]])
