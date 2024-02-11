from aiogram.types import CallbackQuery


def check_winner(cb: CallbackQuery, winner=None):
    check_kb = cb.message.reply_markup.inline_keyboard
    check_kb = [list(map(lambda x: x.text,row)) for row in check_kb]

    # проверка строчек.
    winner = (not winner and
            any(row == [(win := '✕')] * 3 or row == [(win := 'O')] * 3 for row in check_kb)
                     and win or winner)
    # проверка столбцов
    winner = (not winner and
                     any(row == [(win := '✕')] * 3 or row == [(win := 'O')] * 3 for row in (list(row) for row in zip(*check_kb)))
                     and win or winner)

    # вспомогательная строчка с значениями главной диагонали
    main_d = not winner and ''.join([check_kb[i][i] for i in range(3)])
    # вспомогательная строчка с значениями побочной диагонали
    side_d = not winner and ''.join([check_kb[i][i] for i in range(2, -1, -1)])

    # проверяем диагонали.
    winner = not winner and (main_d == (win := 'X') * 3 or main_d == (win := 'O') * 3
                                           or side_d == (win := 'X') * 3 or side_d == (win := 'O') * 3) and win or winner
    # проверка на ничью
    winner = not winner and all(x != '◻️' for row in check_kb for x in row) and 'Ничья' or winner

    return winner

