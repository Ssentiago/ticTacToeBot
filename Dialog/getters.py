from aiogram import Dispatcher
from aiogram_dialog import DialogManager


async def get_sign(dialog_manager: DialogManager, **middlware_data) -> dict:
    ctx = dialog_manager.current_context().dialog_data
    sign = ctx.get('playing_now')
    return {'playing_now': sign}
