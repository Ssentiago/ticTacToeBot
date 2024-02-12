from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

game_field = InlineKeyboardMarkup(inline_keyboard=
                                  [[InlineKeyboardButton(callback_data=f'({row}, {col})', text='◻️')
                                    for col in range(3)]
                                   for row in range(3)])


def create_inline_keyboard(width: int,
                           *args, **kwargs) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    buttons = []
    if args:
        for button in args:
            buttons.append(InlineKeyboardButton(text=button, callback_data=button))
    if kwargs:
        for button, text in kwargs.items():
            buttons.append(InlineKeyboardButton(text=text, callback_data=button))

    kb_builder.row(*buttons, width=width)

    return kb_builder.as_markup()


