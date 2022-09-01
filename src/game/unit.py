from __future__ import annotations
from typing import Dict
import random


from .item import ItemType, Item, Weapon, WeaponRange
from .unit_info import Stats, Class, SupportBonuses, AttributeTypes
from .affinity import Affinity
from scraper.utils import stat_names
import utils
from extensions import GBASprite


class Character(GBASprite):
    """Holds all information about a unit, including its sprites, stats and weapons"""

    def __init__(
        self,
        img,
        batch,
        group,
        level=1,
        stats: Stats = None,
        class_type: Class = None,
        inventory=None,
        team=0,
        default_level=1,
        name="",
        current_hp=1,
        supports: Dict = dict(),
        affinity: Affinity = None,
        is_male: bool = True,
    ):

        # adjusts unit animation frames to correct size
        if hasattr(img, "frames"):
            adjusted_size = utils.TILE_SCALE * utils.TILE_SIZE
            for frame in img.frames:
                frame.image.height = adjusted_size
                frame.image.width = adjusted_size
        super().__init__(img=img, batch=batch, group=group)

        self.name = name
        # Used for game classes (eg. paladin, assassin, etc.)
        self.class_type = class_type  # Class({0: 1, 1: 3}, 0, 0, 0)
        self.class_type = Class({0: 1, 1: 3}, 0, 0)

        # Individual based stats
        # self.battle_sprite = pyglet.sprite.Sprite() # used for battle animation
        self.level = level
        self.default_level = default_level
        self.stats = stats
        if stats is None:
            self.stats = Stats()
        self.current_hp = min(current_hp, self.stats.hp)

        self.items: list[Item] = inventory or []  # will need to filter out non weapons
        self.growths = Stats()
        self.team = team  # Probably use ints for team numbers

        self.weapon_ranks = {}

        self.affinity = affinity
        self.supports = supports  # character object key, support level items
        self.support_bonuses = (
            SupportBonuses()
        )  # bonuses from supports, calculated frequently

        self.temp_stats = Stats()  # represents temporary stat changes
        self.gained_stats = Stats()  # represents stat boosting items

        self.carried_unit = None
        self.is_carried = False

        self.is_male = is_male

    def is_usable_weapon(self, weapon: Item) -> bool:
        """
        Sees if the current character can use an item as a weapon

        Args:
            weapon (Item): item being examined

        Returns:
            bool: indicates whether the item is valid
        """
        # TODO expand on this validation
        return weapon.item_type == ItemType.WEAPON

    def get_equipped_weapon_index(self) -> int:
        """
        Finds index of first usable weapon

        Returns:
            int: Index if found, -1 if not
        """
        for index, item in enumerate(self.items):
            if self.is_usable_weapon(item):
                return index
        # if there are no valid weapons in inventory, return -1
        return -1

    def get_equipped_weapon(self) -> Weapon:
        """
        Gets first weapon in inventory

        Returns:
            Weapon: weapon object that is being equipped
        """
        index = self.get_equipped_weapon_index()

        return self.items[index] if index >= 0 else index

    def get_weapon_range(self) -> WeaponRange:
        """
        Gets range of equipped weapon

        Returns:
            WeaponRange: equipped weapon's range or 0 range if there isn't one
        """
        equipped_weapon = self.get_equipped_weapon()
        return equipped_weapon.weapon_range if equipped_weapon else WeaponRange(0, 0)

    def equip_weapon(self, inventory_slot: int) -> None:
        """Changes the current equipped weapon

        Args:
            inventory_slot (int): Index of desired weapon
        """
        current_equipped = self.get_equipped_weapon_index()
        self.items[current_equipped], self.items[inventory_slot] = (
            self.items[inventory_slot],
            self.items[current_equipped],
        )

    def add_item(self, item: Item) -> bool:
        """
        Adds an item to the character's inventory

        Args:
            item (Item): Item to be added

        Returns:
            bool: success if there is room in the character's inventory
        """
        if len(self.items) < 5:
            self.items.append(item)
            return True
        return False

    @staticmethod
    def get_growth_stat_increase(percentage: int) -> int:
        """
        Gets stat growth from a given percentage

        Args:
            percentage (int): Chance of increasing the stat

        Returns:
            int: Amount that the stat changes
        """
        base = percentage // 100
        return base + (random.randint(1, 100) <= base % 100)

    def level_up(self) -> None:
        """
        Updates stats after growths
        """
        # TODO need to account for level maxes
        self.level += 1

        # TODO need to account for stat maxes
        new_stats = [
            prev_stat + Character.get_growth_stat_increase(percentage)
            for prev_stat, percentage in zip(self.stats, self.growths)
        ]
        self.stats = Stats(*new_stats)

    def change_level(self, new_level: int) -> None:
        """
        Calculates average stats based on given level and growths

        Args:
            new_level (int): Desired level
        """
        # Only changes level if new_level is higher than base level
        if self.default_level >= new_level:
            return
        level_diff = new_level - self.default_level

        for stat in stat_names:
            self.stats[stat] = int(level_diff * self.growths[stat] / 100)

    def take_damage(self, damage: int) -> bool:
        """Applies damage to the character

        Args:
            damage (int): amount of damage

        Returns:
            bool: whether the unit dies or not
        """
        self.current_hp -= damage
        return self.current_hp <= 0

    def character_moved(self) -> None:
        """
        Handles changes that occur after a character moves
        """
        self.color = utils.GRAY_TINT

    def refresh(self) -> None:
        """
        Handles changes that occur after a character gains their move
        """
        self.color = utils.NORMAL_TINT

    def calc_aid(self) -> int:
        """
        Used to calculate the aid based on mount and con

        Returns:
            int: Aid value used for rescue calculation
        """
        con = self.stats.con
        if self.class_type.class_attributes.get(AttributeTypes.IS_MOUNTED, False):
            if self.is_male:
                return 25 - con
            return 20 - con
        return con - 1

    def carry_unit(self, carried: Character) -> None:
        """
        Handles logic for this unit to carry another

        Args:
            carried (Character): unit being carried
        """
        self.carried_unit = carried
        carried.is_carried = True
