import random

from .unit import Character
from .item import Weapon, WeaponRank


def attack_speed(selected_unit: Character):
    """Calculates a character's effective attack speed

    Returns:
        [type]: [description]
    """
    equipped_weapon = selected_unit.get_equipped_weapon()
    speed = selected_unit.stats.spd
    if equipped_weapon:
        burden = selected_unit.stats.con - equipped_weapon.weight
        if burden < 0:
            return speed + burden
    return speed


def hitrate_calc(attacking_unit: Character):
    """Calculates a character's accuracy disregarding enemy

    Args:
        s_rank (int, optional): [description]. Defaults to 0.

    Returns:
        [type]: [description]
    """
    equipped_weapon = attacking_unit.get_equipped_weapon()
    if equipped_weapon is None:
        return 0

    weapon_acc = equipped_weapon.hit

    support = attacking_unit.support_bonuses.hit_rate

    s_rank = 0
    if attacking_unit.weapon_ranks.get(equipped_weapon.weapon_type) == WeaponRank.S:
        s_rank = 5

    return (
        weapon_acc
        + attacking_unit.stats.skl * 2
        + attacking_unit.stats.lck / 2
        + support
        + s_rank
    )


def avoid_calc(attacked_unit: Character, terrain_bonus=0):
    """Calculates a character's avoidance

    Args:
        terrain_bonus (int, optional): [description]. Defaults to 0.

    Returns:
        [type]: [description]
    """
    return (
        attack_speed(attacked_unit) * 2
        + attacked_unit.stats.lck
        + terrain_bonus
        + attacked_unit.support_bonuses.avoid
    )


def accuracy_calc(attacking_unit: Character, attacked_unit: Character, terrain_bonus):
    """
    Calculates effective accuracy based on hit rate and enemy avoidance
    """

    own_weapon = attacking_unit.get_equipped_weapon()
    if own_weapon is None:
        return 0

    enemy_weapon = attacked_unit.get_equipped_weapon()

    _, triangle_bonus = own_weapon.get_weapon_triangle(enemy_weapon)

    calc = (
        hitrate_calc(attacking_unit)
        - avoid_calc(attacked_unit, terrain_bonus)
        + triangle_bonus
    )

    return 0 if calc < 0 else 100 if calc > 100 else calc


def attack_power(attacking_unit: Character, attacked_unit: Character):
    """Calculates character's attack power

    Args:
        weapon_effectiveness: special attributes (ie bows vs flying)

    Returns:
        [type]: [description]
    """
    strength = attacking_unit.stats.str
    equipped_weapon = attacking_unit.get_equipped_weapon()
    weapon_effectiveness = 1
    if equipped_weapon:
        might = equipped_weapon.might
        triangle_damage, _ = equipped_weapon.get_weapon_triangle(
            attacked_unit.get_equipped_weapon()
        )
        weapon_effectiveness = equipped_weapon.get_weapon_effectiveness(
            attacked_unit.class_type.class_attributes
        )
    else:
        might = 0
        triangle_damage = 0
    support = attacking_unit.support_bonuses.attack
    return strength + (might + triangle_damage) * weapon_effectiveness + support


def defense_power(attacked_unit: Character, terrain_bonus=0, is_magic=False):
    """Calculates character's defense

    Args:
        terrain_bonus (int, optional): [description]. Defaults to 0.
        is_magic (bool, optional): [description]. Defaults to False.

    Returns:
        [type]: [description]
    """
    # need to somehow account for magic vs strength; currently is_magic
    # enemy weapon in WeaponType.SECOND_TRIANGLE
    support = attacked_unit.support_bonuses.defense
    if is_magic:
        return terrain_bonus + attacked_unit.stats.res + support
    return terrain_bonus + attacked_unit.stats.def_ + support


def critrate_calc(attacking_unit: Character):
    """Calculates crit rate in a vacuum

    Args:
        s_rank (int, optional): [description]. Defaults to 0.

    Returns:
        [type]: [description]
    """
    # class critical rates - don't forget them
    equipped_weapon = attacking_unit.get_equipped_weapon()
    weapon_critical = 0
    s_rank = 0
    if equipped_weapon:
        weapon_critical = equipped_weapon.crit_rate
        if attacking_unit.weapon_ranks.get(equipped_weapon.weapon_type) == WeaponRank.S:
            s_rank = 5
    support = attacking_unit.support_bonuses.crit_chance
    return (
        weapon_critical
        + attacking_unit.stats.skl / 2
        + support
        + attacking_unit.class_type.class_crit
        + s_rank
    )


def crit_avoid_calc(attacked_unit: Character):
    """Calculates crit dodge in a vacuum

    Returns:
        [type]: [description]
    """
    return attacked_unit.stats.lck + attacked_unit.support_bonuses.crit_avoid


def crit_accuracy_calc(attacking_unit, attacked_unit: Character):
    """Calculates crit chance based on own crit rate and enemy crit avoid"""
    # between 0 and 100
    # crit rate - crit evade
    return critrate_calc(attacking_unit) - crit_avoid_calc(attacked_unit)


def damage_calc(
    attacking_unit: Character,
    attacked_unit: Character,
    terrain_bonus=0,
    is_magic=False,
    is_crit=False,
):
    """Calculates net damage

    Args:
        enemy ([type]): [description]
    """
    # must be >= 0
    # attack power - defense power
    # crit is 3x above formula
    base = attack_power(attacking_unit, attacked_unit) - defense_power(
        attacked_unit, terrain_bonus, is_magic
    )
    if is_crit:
        base *= 3

    return 0 if base < 0 else base


def determine_hit(percentage):
    return random.randint(0, 100) < percentage
