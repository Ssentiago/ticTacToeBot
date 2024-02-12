from aiogram.fsm.storage.redis import RedisStorage, Redis
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup

redis = Redis(host='localhost')
storage = RedisStorage(redis=redis)


class GameProgress(StatesGroup):
    default = default_state
    game_cycle = State()
    game_end = State()
    multiplayer = State()
