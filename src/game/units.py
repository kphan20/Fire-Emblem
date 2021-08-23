import pyglet
from dataclasses import dataclass
from utils import stat_names
import random

class WeaponClass:
    pass

class Weapon:
    def __init__(self, name="", description='', might=0, weight=0, accuracy=0, weapon_rank=0, crit_rate=0, uses=0, price=0, uses_left=None):
        self.name = name
        self.description = description
        self.might = might
        self.weight = weight
        self.accuracy = accuracy
        self.weapon_rank = weapon_rank
        self.crit_rate = crit_rate
        self.uses = uses
        self.price = price
        self.uses_left = uses_left or uses
    def get_weapon_triangle(self):#, other_weapon):
        return 0
    def decrement_uses_left(self):
        self.uses_left -= 1
    def generate_sell_price(self):
        return self.price * (self.uses_left/self.uses) / 2
# make this a namedtuple?
@dataclass
class Stats:
    """Can double as growths object"""
    #__slots__=('level', 'hp', 'str', 'skl', 'spd', 'lck', 'def_', 'res', 'con', 'mov')
    def __init__(self, level, stats):
        # prolly just change this to an object
        self.level = level
        self.stats = stats

def determine_hit(percentage):
    return random.randint(0, 100) < percentage

class Character(pyglet.sprite.Sprite):
    """Holds all information about a unit, including its sprites, stats and weapons"""
    def __init__(self, img, batch, group, team=0, default_level=1, stats={}, name = ''):
        super().__init__(img=img, batch=batch, group=group)
        
        self.name = name
        # Used for game classes (eg. paladin, assassin, etc.)
        self.class_type = Class({0: 1, 1: 3}, 0, 0)
        # Can be pulled from class_type
        self.valid_weapons = []
        
        # Individual based stats
        #self.battle_sprite = pyglet.sprite.Sprite() # used for battle animation
        self.default_level = default_level
        self.stats = stats # transition to making stats a simple dictionary
        self.weapons = [] # will need to filter out non weapons
        self.growths = {}
        self.team = team # Probably use ints for team numbers
        self.carried_unit = None
        self.equipped_weapon = None
        self.weapon_ranks = {}
        self.personal_weapon = None
        
    def equip_weapon(self, inventory_slot):
        """Changes the current equipped weapon

        Args:
            inventory_slot (int): Index of desired weapon
        """
        # will need to rework logic for this for scouting damage/inventory management
        self.equipped_weapon = self.weapons[inventory_slot]
        
    def find_supports(self):
        """Finds supports nearby

        Returns:
            [type]: [description]
        """
        return 0
    
    def attack_speed(self):
        """Calculates a character's effective attack speed

        Returns:
            [type]: [description]
        """
        equipped_weapon = self.equipped_weapon
        speed = self.stats.spd
        if equipped_weapon:
            burden = self.stats.con - equipped_weapon.weight
            if burden < 0:
                return speed + burden
        return speed

    def hitrate_calc(self, s_rank=0):
        """Calculates a character's accuracy in a vacuum

        Args:
            s_rank (int, optional): [description]. Defaults to 0.

        Returns:
            [type]: [description]
        """
        equipped_weapon = self.equipped_weapon
        if equipped_weapon:
            weapon_acc = equipped_weapon.accuracy
        else:
            return 0
        support = self.find_supports()
        return weapon_acc + self.stats.skl * 2 + self.lck / 2 + support + s_rank
    
    def avoid_calc(self, terrain_bonus=0):
        """Calculates a character's avoidance

        Args:
            terrain_bonus (int, optional): [description]. Defaults to 0.

        Returns:
            [type]: [description]
        """
        return self.attack_speed() * 2 + self.stats.lck + terrain_bonus + self.find_supports()
    
    def accuracy_calc(self, enemy, triangle_bonus=0):
        """Calculates effective accuracy based on hit rate and enemy avoidance

        Args:
            enemy ([type]): [description]
            triangle_bonus (int, optional): [description]. Defaults to 0.
        """
        # must be 0-100
        # hit rate - avoid + triangle bonus
        pass
    
    def attack_power(self, weapon_effectiveness, reaver=1):
        """Calculates character's attack power

        Args:
            weapon_effectiveness ([type]): [description]
            reaver (int, optional): [description]. Defaults to 1.

        Returns:
            [type]: [description]
        """
        strength = self.stats.str
        equipped_weapon = self.equipped_weapon
        if equipped_weapon:
            might = equipped_weapon.might or 0 # remove this later
            weapon_triangle = equipped_weapon.get_weapon_triangle()
        else:
            might = 0
            weapon_triangle = 0
        support = self.find_supports()
        return strength + (might + weapon_triangle) * weapon_effectiveness + support
    
    def defense_power(self, terrain_bonus=0, is_magic=False):
        """Calculates character's defense

        Args:
            terrain_bonus (int, optional): [description]. Defaults to 0.
            is_magic (bool, optional): [description]. Defaults to False.

        Returns:
            [type]: [description]
        """
        # need to somehow account for magic vs strength; currently is_magic
        support = self.find_supports()
        if is_magic:
            return terrain_bonus + self.stats.res + support
        return terrain_bonus + self.stats.def_ + support
    
    def critrate_calc(self, s_rank=0):
        """Calculates crit rate in a vacuum

        Args:
            s_rank (int, optional): [description]. Defaults to 0.

        Returns:
            [type]: [description]
        """
        # class critical rates - don't forget them
        equipped_weapon = self.equipped_weapon
        weapon_critical = 0
        if equipped_weapon:
            weapon_critical = equipped_weapon.crit_rate
        support = self.find_supports()
        return weapon_critical + self.stats.skl / 2 + support + s_rank
    
    def crit_avoid_calc(self):
        """Calculates crit dodge in a vacuum

        Returns:
            [type]: [description]
        """
        return self.stats.lck + self.find_supports()
    
    def crit_accuracy_calc(self):
        """Calculates crit chance based on own crit rate and enemy crit avoid
        """
        # between 0 and 100
        # crit rate - crit evade
        pass
    
    def damage_calc(self, enemy):
        """Calculates net damage

        Args:
            enemy ([type]): [description]
        """
        # must be >= 0
        # attack power - defense power
        # crit is 3x above formula
        pass
    
    def change_level(self, new_level):
        """Calculates average stats based on given level and growths

        Args:
            new_level (int): Desired level
        """
        # Only changes level if new_level is higher than base level
        if (self.default_level >= new_level):
            return
        level_diff = new_level - self.default_level
        for stat in stat_names:
            self.stats[stat] = level_diff * self.growths[stat] / 100

@dataclass
class Class:
    """Will be used to categorize units"""
    __slots__ =('terrain_cost', 'mov', 'con', 'classname')
    def __init__(self, terrain_cost, mov, con, classname=''):
        self.terrain_cost = terrain_cost
        self.mov = mov
        self.con = con
        self.classname = classname
    def set_classname(self, name):
        self.classname=name
    def calc_aid(self):
        """Used to calculate the aid based on mount and con

        Returns:
            int: Aid value used for rescue calculation
        """
        return self.con - 1