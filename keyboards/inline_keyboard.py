from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from filters.core_filters import CellsCallbackFactory


class TTTKeyboard:
    @staticmethod
    def create_game_field(size: int):
        game_field = InlineKeyboardMarkup(inline_keyboard=
                                          [[InlineKeyboardButton(text='◻️', callback_data=CellsCallbackFactory(x=row,
                                                                                                               y=col).pack())
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
