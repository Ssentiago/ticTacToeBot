from aiogram.filters.callback_data import CallbackData


class CellsCallbackFactory(CallbackData, prefix=''):
    x: int
    y: int

