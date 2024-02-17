from aiogram.filters.callback_data import CallbackData


class CellsCallbackFactory(CallbackData, prefix='Coordinates', sep='_'):
    x: int
    y: int

