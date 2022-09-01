import random

from .unit import Character
from .item import WeaponRank


def clamp_percentage(calc: float) -> float:
    """
    Helper function to clamp functions that output a percentage

    Args:
        calc (float): value to be clamped

    Returns:
        float: final value
    """
    return 0 if calc < 0 else 100 if calc > 100 else calc


def attack_speed(selected_unit: Character) -> int:
    """
    Calculates a character's effective attack speed

    Args:
        selected_unit (Character): unit for calculation

    Returns:
        int: net speed for the selected unit
    """
    equipped_weapon = selected_unit.get_equipped_weapon()
    speed = selected_unit.stats.spd

    # handles case where weapon is larger than con
    if equipped_weapon:
        burden = selected_unit.stats.con - equipped_weapon.weight
        if burden < 0:
            return speed + burden

    return speed


def hitrate_calc(attacking_unit: Character) -> float:
    """
    Calculates a character's accuracy disregarding enemy

    Args:
        attacking_unit (Character): unit that's attacking another

    Returns:
        float: hitrate in a vacuum
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


def avoid_calc(attacked_unit: Character, terrain_bonus=0) -> float:
    """
    Calculates a character's avoidance

    Args:
        attacking_unit (Character): unit that is being attacked
        terrain_bonus (int, optional): Avoid bonus from terrain. Defaults to 0.

    Returns:
        float: Avoidance for attacked unit
    """
    return (
        attack_speed(attacked_unit) * 2
        + attacked_unit.stats.lck
        + terrain_bonus
        + attacked_unit.support_bonuses.avoid
    )


def accuracy_calc(
    attacking_unit: Character, attacked_unit: Character, terrain_bonus: int
) -> float:
    """
    Calculates chance of one unit hitting another

    Returns:
        float: Net percentage of attacked unit being hit
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

    return clamp_percentage(calc)


def attack_power(attacking_unit: Character, attacked_unit: Character) -> float:
    """
    Calculates raw attack strength

    Returns:
        float: final calculation after weapon effectiveness and other factors
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


def defense_power(attacked_unit: Character, terrain_bonus=0, is_magic=False) -> float:
    """
    Calculates attacked unit's damage reduction

    Args:
        attacked_unit (Character): unit being attacked
        terrain_bonus (int, optional): defense bonus from terrain. Defaults to 0.
        is_magic (bool, optional): whether the incoming attack is magic based or not. Defaults to False.

    Returns:
        float: damage reduction after all bonuses
    """
    # need to somehow account for magic vs strength; currently is_magic
    # enemy weapon in WeaponType.SECOND_TRIANGLE
    support = attacked_unit.support_bonuses.defense
    if is_magic:
        return terrain_bonus + attacked_unit.stats.res + support
    return terrain_bonus + attacked_unit.stats.def_ + support


def critrate_calc(attacking_unit: Character) -> float:
    """
    Raw chance for character to crit

    Returns:
        float: crit percentage in a vacuum
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


def crit_avoid_calc(attacked_unit: Character) -> float:
    """
    Calculates crit dodge in a vacuum

    Returns:
        float: character's inherent resistance to being crit
    """
    return attacked_unit.stats.lck + attacked_unit.support_bonuses.crit_avoid


def crit_accuracy_calc(attacking_unit: Character, attacked_unit: Character) -> float:
    """Calculates crit chance based on own crit rate and enemy crit avoid"""
    return clamp_percentage(
        critrate_calc(attacking_unit) - crit_avoid_calc(attacked_unit)
    )


def damage_calc(
    attacking_unit: Character,
    attacked_unit: Character,
    terrain_bonus=0,
    is_magic=False,
    is_crit=False,
) -> float:
    """
    Calculates net damage after defense calculation

    Returns:
        float: net damage after attack, defense, and crit calculations
    """
    base = attack_power(attacking_unit, attacked_unit) - defense_power(
        attacked_unit, terrain_bonus, is_magic
    )
    if is_crit:
        base *= 3

    # damage is floored at 0
    return 0 if base < 0 else base


def determine_hit(percentage: float, two_rn: bool = False) -> bool:
    """
    Given a percentage, decides if a character hits their attack

    Args:
        percentage (float): threshold for a success
        two_rn (bool, optional):
            flag to indicate if the success calculation is based on an average or not. Defaults to False.

    Returns:
        bool: success or miss
    """
    if two_rn:
        return (random.randint(0, 100) + random.randint(0, 100)) // 2 < percentage
    return random.randint(0, 100) < percentage
