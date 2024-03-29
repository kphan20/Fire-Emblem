from enum import Enum


class ViewState(Enum):
    NOTHING_SELECTED = 0
    MOVEMENT = 1
    OPTION_MENU = 2
    TRADE_SELECTED = 3
    WEAPON_SELECTION = 4
    ATTACK_SELECTION = 5
    TURN_MENU = 6
    INVENTORY_MENU = 7
    RESCUE_MENU = 8
    TAKE_MENU = 9
    TRADE_SELECTION = 10
    GIVE_MENU = 11
    DROP_MENU = 12
