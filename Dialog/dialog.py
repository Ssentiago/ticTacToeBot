from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Button, Group, SwitchTo
from aiogram_dialog.widgets.text import Const
from aiogram_dialog import Dialog

from Dialog.getters import get_sign
from Dialog.on_clickers import on_click_field, on_click_two_p
from lexicon.lexicon import lexicon
from states.states import Game
from handlers.core_handlers import TTTKeyboard

main_window = Window(
    Const(lexicon.start),
    SwitchTo(Const('Начать'), id = 'begin', state = Game.mode),
    SwitchTo(Const('Правила'), id = 'rules', state = Game.rules),
    state = Game.start
)
rule_window = Window(Const(lexicon.rules),
                     SwitchTo(Const('Вернуться'), id = 'back', state = Game.start),
                     state = Game.rules)

mode_window = Window(Const(lexicon.mode),
                     Button(Const('Один игрок: компьютер'), id = 'player_vs_computer'),
                     Button(Const('Один игрок: другой игрок'), id = 'player_vs_player'),
                     SwitchTo(Const('Два игрока'), id = 'two_players_on_one_computer', state = Game.game_process,
                              on_click = on_click_two_p),
                     state = Game.mode)

game_process_window = Window(Const('Игра началась! Сейчас ходит - Крестик!'),
                             Group(*TTTKeyboard.create_game_field(3, on_click = on_click_field), width = 3),
                             state = Game.game_process,
                             getter = get_sign)

main_menu = Dialog(main_window, rule_window, mode_window, game_process_window)
