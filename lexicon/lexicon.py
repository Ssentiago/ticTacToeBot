from dataclasses import dataclass


@dataclass
class lexicon:
    start: str = '''Приветствую! Я простой бот для игры в крестики и нолики!

Нажми кнопку "Начать", чтобы перейти к выбору режима игры.
Если ты хочешь узнать правила игры, то нажми кнопку "Правила"'''

    rules: str = '''Один из игроков играет «крестиками», второй — «ноликами».
Игроки по очереди ставят на свободные клетки поля 3х3 знаки (один всегда крестики, другой всегда нолики).
 Первый, выстроивший в ряд 3 своих фигур по вертикали, горизонтали или диагонали, выигрывает. Первый ход делает игрок, ставящий крестики.'''
    mode: str = '''Выберите режим игры:
"Один игрок: компьютер" - проявите свои навыки против компьютера! Сумеете ли вы одержать верх над бездушной машиной?
"Один игрок: другой игрок" - сразитесь с другим игроком. Попытайте удачу, проявите все свои самые лучшие качества - одержите победу над другим игроком или падите ниц!
"Два игрока" - сыграйте вместе с другим человеком на одном компьютере!'''