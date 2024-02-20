from dataclasses import dataclass


@dataclass
class Cell:
    x: int
    y: int
    text: str


async def get_empty_cell(line: list[Cell]) -> tuple[int, int]:
    for cell in line:
        if cell.text == '◻️':
            return cell.x, cell.y

class Service:
    signs = {'✕': 'Крестик', 'O': 'Нолик'}
    game_pool = {'pool': {}, 'pairs': set()}
