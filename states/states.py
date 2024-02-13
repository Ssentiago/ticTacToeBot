from aiogram.fsm.storage.redis import RedisStorage, Redis
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup

redis = Redis(host='localhost')
storage = RedisStorage(redis=redis)


# все возможные состояния пользователей
class Game(StatesGroup):
    default = default_state
    two_players_on_one_computer = State()
    player_vs_computer = State()
    player_vs_player = State()
    end_of_game = State()