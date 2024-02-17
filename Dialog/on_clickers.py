from pprint import pprint

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button


async def on_click_field(cb: CallbackQuery, button: Button, manager: DialogManager):
    x, y = map(int, cb.data.split('_'))
    ctx = manager.current_context()







async def on_click_two_p(cb: CallbackQuery, button: Button, manager: DialogManager):
    ctx = manager.current_context()
    ctx.dialog_data.update(sign='X')

