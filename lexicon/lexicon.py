from dataclasses import dataclass


@dataclass
class lexicon:
    start: str = '''Приветствую! Я простой бот для игры в крестики и нолики!

Нажми кнопку "Начать", чтобы перейти к выбору режима игры.

Или, если ты хочешь узнать правила игры, то нажми кнопку "Правила"'''

    rules: str = '''Один из игроков играет «крестиками», второй — «ноликами».
    
Игроки по очереди ставят на свободные клетки поля 3х3 знаки (один всегда крестики, другой всегда нолики).

 Первый игрок, который выстроит в ряд 3 свои фигуры по вертикали, горизонтали или диагонали, выигрывает.
 
 Первый ход делает игрок, ставящий крестики.'''
    mode: str = '''Выберите режим игры:
"Компьютер" - Испытай свои навыки в сражении с компьютерным противником! В этом режиме ты сможешь сразиться с интеллектом машины и проверить свои стратегические навыки в игре в крестики-нолики. Сумеешь ли ты обойти алгоритм и одержать победу?

"Игра против другого игрока" - Вступите в битву с случайным соперником и докажи своё мастерство в игре в крестики-нолики! В этом напряженном соревновании ты столкнешься с игроками со всего мира. Покажи свою логику и стратегическое мышление, чтобы одержать победу и подняться на вершину рейтинга!

"На двоих" - Пригласите друга и сыграйте в крестики-нолики на одном экране! Попробуйте обойти друг друга в этой стратегической битве, ставя крестики и нолики на поле. Узнайте, кто из вас окажется лучшим в этой интеллектуальной дуэли, где каждый ход может решить судьбу игры!'''
    game_process = lambda sign, next_sign: f'{sign} сделал свой ход! Теперь ходит {next_sign}!'
    cancel = '''Игра была отменена! Жаль!..'''
    game_start = lambda sign: f'Игра началась! Вы - {sign}! Ходит Крестик!'

    mode_rating = '''Выберите один из пунктов меню:
"Поиск игроков" - начать поиск соперников
"Рейтинг" - узнать текущее положение в рейтинге и лидеров '''


    @classmethod
    def rating(cls, user_rate, last_ten_rates):
        raw_data = '\n'.join(f'{x[1]}: {x[2]} побед' for x in last_ten_rates)
        return f'''Ваш личный рейтинг: {user_rate}
        
<b>Топ 10 игроков</b>:
{raw_data}    
    '''