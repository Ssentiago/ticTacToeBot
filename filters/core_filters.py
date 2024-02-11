from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery


class FilterCellsCBData(BaseFilter):
    async def __call__(self, cb: CallbackQuery):
        obj = eval(cb.data)
        if obj.__class__ == tuple:
            return {'coords': obj}
        return False
