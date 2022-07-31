from __future__ import annotations
from enum import Enum


class ItemType(Enum):
    WEAPON = 1
    HEAL_STAVE = 2
    ENEMY_STAVE = 3
    CONSUMABLE = 4


class WeaponRank(Enum):
    E = 0
    D = 1
    C = 2
    B = 3
    A = 4
    S = 5


class WeaponType(Enum):
    SWORD = 0
    LANCE = 1
    AXE = 2
    BOW = 3
    STAVE = 4
    ANIMA = 5
    DARK = 6
    LIGHT = 7
    MONSTER = 8
    FIRST_TRIANGLE = {SWORD: (AXE, LANCE), LANCE: (SWORD, AXE), AXE: (LANCE, SWORD)}
    SECOND_TRIANGLE = {ANIMA: (LIGHT, DARK), DARK: (ANIMA, LIGHT), LIGHT: (DARK, ANIMA)}


class ClassAttributes(Enum):
    IS_FLIER = "IS_FLIER"
    IS_MOUNTED = "IS_MOUNTED"
    IS_ARMORED = "IS_ARMORED"
    IS_DRAGON = "IS_DRAGON"
    IS_SWORD_CLASS = "IS_SWORD_CLASS"
    IS_MONSTER = "IS_MONSTER"
    IS_DARK_DRUID = "IS_DARK_DRUID"


class Item:
    def __init__(self, uses, value, effects, item_type: ItemType, uses_left=None):
        self.uses = uses
        self.value = value
        self.effects = effects
        self.item_type = item_type
        self.uses_left = uses_left if uses_left is not None else uses

    def use(self):
        self.uses_left -= 1

    def generate_sell_price(self):
        return self.value * (self.uses_left / self.uses) / 2


class WeaponRange:
    def __init__(self, min_range, max_range):
        self.min_range = min_range
        self.max_range = max_range


class Weapon(Item):
    def __init__(
        self,
        uses: int,
        value: int,
        weapon_type: WeaponType,
        effects=None,
        name="",
        description="",
        might=0,
        weight=0,
        hit=0,
        weapon_rank=WeaponRank.E,
        crit_rate=0,
        uses_left=None,
        weapon_exp=0,
        personal_weapon_owner=None,
        is_reaver=False,
        weapon_range=None,
    ):
        super().__init__(uses, value, effects, ItemType.WEAPON, uses_left)
        self.weapon_type = weapon_type
        self.name = name
        self.description = description
        self.might = might
        self.weight = weight
        self.hit = hit
        self.weapon_rank = weapon_rank
        self.crit_rate = crit_rate
        self.weapon_exp = weapon_exp
        self.personal_weapon_owner = personal_weapon_owner
        self.is_reaver = is_reaver
        self.weapon_attributes = (
            {}
        )  # will have attribute name keys and multipliers items
        self.weapon_range = weapon_range
        if weapon_range is None:
            self.weapon_range = WeaponRange(1, 1)

    def get_weapon_triangle(self, other_weapon: Weapon):
        """Returns weapon triangle damage and accuracy boost

        Args:
            other_weapon (Weapon): _description_

        Returns:
            _type_: _description_
        """
        if other_weapon is None or self.weapon_type == other_weapon.weapon_type:
            return 0, 0
        if (
            self.weapon_type in WeaponType.FIRST_TRIANGLE
            and other_weapon.weapon_type in WeaponType.FIRST_TRIANGLE
        ):
            weapon_triangle = WeaponType.FIRST_TRIANGLE
        elif (
            self.weapon_type in WeaponType.SECOND_TRIANGLE
            and other_weapon.weapon_type in WeaponType.SECOND_TRIANGLE
        ):
            weapon_triangle = WeaponType.SECOND_TRIANGLE
        else:
            return 0, 0
        if weapon_triangle[self.weapon_type][0] == other_weapon.weapon_type:
            damage = 1
            accuracy = 15
        else:
            damage = -1
            accuracy = -15
        reaver_multiplier = -2 * (self.is_reaver ^ other_weapon.is_reaver)
        damage *= reaver_multiplier
        accuracy *= reaver_multiplier
        return damage, accuracy

    def get_weapon_effectiveness(self, attribute_dict):
        weapon_effectiveness = 1
        for attribute, multiplier in self.weapon_attributes.items():
            if attribute_dict.get(attribute):
                weapon_effectiveness *= multiplier
        return weapon_effectiveness
