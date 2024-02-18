from dataclasses import dataclass


@dataclass
class Cell:
    x: int
    y: int
    text: str

class Service:
    signs = {'✕': 'Крестик', 'O': 'Нолик'}
    game_pool = {'pool': {}, 'pairs': set()}