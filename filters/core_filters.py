from aiogram.filters.callback_data import CallbackData


class CellsCallbackFactory(CallbackData, prefix='Coordinates'):
    x: int
    y: int

