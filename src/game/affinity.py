from enum import Enum
from .unit_info import SupportBonuses


class Affinity(Enum):
    FIRE = 0
    THUNDER = 1
    WIND = 2
    ICE = 3
    DARK = 4
    LIGHT = 5
    ANIMA = 6


affinity_bonuses = {
    Affinity.FIRE: SupportBonuses(attack=0.5, hit_rate=2.5, avoid=2.5, crit_chance=2.5),
    Affinity.THUNDER: SupportBonuses(
        defense=0.5, avoid=2.5, crit_chance=2.5, crit_avoid=2.5
    ),
    Affinity.WIND: SupportBonuses(
        attack=0.5, hit_rate=2.5, crit_chance=2.5, crit_avoid=2.5
    ),
    Affinity.ICE: SupportBonuses(defense=0.5, hit_rate=2.5, avoid=2.5, crit_avoid=2.5),
    Affinity.DARK: SupportBonuses(
        hit_rate=2.5, avoid=2.5, crit_chance=2.5, crit_avoid=2.5
    ),
    Affinity.LIGHT: SupportBonuses(
        attack=0.5, defense=0.5, hit_rate=2.5, crit_chance=2.5
    ),
    Affinity.ANIMA: SupportBonuses(attack=0.5, defense=0.5, avoid=2.5, crit_avoid=2.5),
    None: SupportBonuses(),
}


def get_affinity_bonus(aff1, aff2):
    return affinity_bonuses[aff1] + affinity_bonuses[aff2]
