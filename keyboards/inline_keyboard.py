from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const



class TTTKeyboard:
    @staticmethod
    def create_game_field(size: int, on_click):
        game_field = [Button(Const('◻️'), id=f"{row}_{col}", on_click=on_click) for row in range(3) for col in range(3)]
        return game_field





        # game_field = InlineKeyboardMarkup(inline_keyboard=
        #                                   [[InlineKeyboardButton(text='◻️', callback_data=CellsCallbackFactory(x=row,
        #                                                                                                        y=col).pack())
        #                                     for col in range(size)]
        #                                    for row in range(size)])
        # return game_field

    # @staticmethod
    # def create_simple_inline_keyboard(width: int,
    #                                   *args, **kwargs) -> InlineKeyboardMarkup:
    #     kb_builder = InlineKeyboardBuilder()
    #     buttons = []
    #     if args:
    #         for button in args:
    #             buttons.append(InlineKeyboardButton(text=button, callback_data=button))
    #     if kwargs:
    #         for button, text in kwargs.items():
    #             buttons.append(InlineKeyboardButton(text=text, callback_data=button))
    #
    #     kb_builder.row(*buttons, width=width)
    #
    #     return kb_builder.as_markup()
