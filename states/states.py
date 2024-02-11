from aiogram.fsm.storage.redis import RedisStorage, Redis
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from itertools import cycle

redis = Redis(host='localhost')
storage = RedisStorage(redis=redis)


class GameProgress(StatesGroup):
    game_start = State()
    game_cycle = cycle([State(state='Крестик'), State(state='Нолик')])
    game_end = State()


