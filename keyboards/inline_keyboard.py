from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class TTTKeyboard:
    @staticmethod
    def create_game_field(size):
        game_field = InlineKeyboardMarkup(inline_keyboard=
                                          [[InlineKeyboardButton(callback_data=f'({row}, {col})', text='◻️')
                                            for col in range(size)]
                                           for row in range(size)])
        return game_field

    @staticmethod
    def create_simple_inline_keyboard(width: int,
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
