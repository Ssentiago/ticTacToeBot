# получаем выигрышные линии - горизонтали, вертикали и диагонали для удобной с ними работы
from aiogram.types import CallbackQuery

from service.service import Cell


async def get_winner_lines(cb: CallbackQuery):
    kb = [list(map(lambda x: x.text, row)) for row in cb.message.reply_markup.inline_keyboard]
    for ind, row in enumerate(kb):
        for elem_ind, elem in enumerate(row):
            kb[ind][elem_ind] = Cell(ind, elem_ind, elem)

    hor = [x for x in kb]
    vert = [x for x in [list(i) for i in zip(*kb)]]
    d1 = [kb[i][i] for i in range(3)]
    d2 = [kb[2 - i][i] for i in range(2, -1, -1)]
    diag = [d1, d2]
    res = []
    res.extend(hor)
    res.extend(vert)
    res.extend(diag)
    return res


# проверяем что хотя бы на одной из выигрышных линий есть символы одного из игроков
# если ни на одной линии нет пустой клетки - то ничья
async def check_winner(cb: CallbackQuery, winner = None):
    lines = [[elem.text for elem in row] for row in (await get_winner_lines(cb))]
    winner = winner is None and any(x.count('✕') == 3 for x in lines) and '✕' or winner
    winner = winner is None and any(x.count('O') == 3 for x in lines) and 'O' or winner
    winner = winner is None and all(x.count('◻️') == 0 for x in lines) and 'Ничья' or winner
    return winner
