import pyglet

class WeaponClass:
    pass

class Weapon:
    def __init__(self, name="",might=0, weight=0, accuracy=0, weapon_rank=0, crit_rate=0):
        self.name = name
        self.might = might
        self.weight = weight
        self.accuracy = accuracy
        self.weapon_rank = weapon_rank
        self.crit_rate = crit_rate
    def get_weapon_triangle(self):#, other_weapon):
        return 0
# make this a namedtuple?
class Stats:
    """Can double as growths object"""
    __slots__=('level', 'hp', 'str', 'skl', 'spd', 'lck', 'def_', 'res', 'con', 'mov')
    def __init__(self, level, hp, str, skl, spd, lck, def_, res, con, mov):
        self.level = level
        self.hp = hp
        self.str = str
        self.skl = skl
        self.spd = spd
        self.lck = lck
        self.def_ = def_
        self.res = res
        self.con = con
        self.mov = mov
        
class Character(pyglet.sprite.Sprite):
    """Holds all information about a unit, including its sprites, stats and weapons"""
    def __init__(self, img, batch, group, team=0, stats=Stats(0, -1, 0, 0, 0, 0, 0, 0, 0, 0)):
        super().__init__(img=img, batch=batch, group=group)
        
        # Used for game classes (eg. paladin, assassin, etc.)
        self.class_type = Class({0: 1, 1: 3})
        # Can be pulled from class_type
        self.valid_weapons = []
        
        # Individual based stats
        #self.battle_sprite = pyglet.sprite.Sprite() # used for battle animation
        self.stats = stats
        self.weapons = [] # will need to filter out non weapons
        self.growths = {}
        self.team = team # Probably use ints for team numbers
        self.carried_unit = None
        self.equipped_weapon = None
        self.weapon_ranks = {}
        
    def equip_weapon(self, inventory_slot):
        # will need to rework logic for this for scouting damage/inventory management
        self.equipped_weapon = self.weapons[inventory_slot]
    def find_supports(self):
        return 0
    def attack_speed(self):
        equipped_weapon = self.equipped_weapon
        speed = self.stats.spd
        if equipped_weapon:
            burden = self.stats.con - equipped_weapon.weight
            if burden < 0:
                return speed + burden
        return speed
    def hitrate_calc(self, s_rank=0):
        equipped_weapon = self.equipped_weapon
        if equipped_weapon:
            weapon_acc = equipped_weapon.accuracy
        else:
            return 0
        support = self.find_supports()
        return weapon_acc + self.stats.skl * 2 + self.lck / 2 + support + s_rank
    def avoid_calc(self, terrain_bonus=0):
        return self.attack_speed() * 2 + self.stats.lck + terrain_bonus + self.find_supports()
    def accuracy_calc(self, enemy, triangle_bonus=0):
        # must be 0-100
        # hit rate - avoid + triangle bonus
        pass
    def attack_power(self, weapon_effectiveness, reaver=1):
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
        # need to somehow account for magic vs strength; currently is_magic
        support = self.find_supports()
        if is_magic:
            return terrain_bonus + self.stats.res + support
        return terrain_bonus + self.stats.def_ + support
    def critrate_calc(self, s_rank=0):
        # class critical rates - don't forget them
        equipped_weapon = self.equipped_weapon
        weapon_critical = 0
        if equipped_weapon:
            weapon_critical = equipped_weapon.crit_rate
        support = self.find_supports()
        return weapon_critical + self.stats.skl / 2 + support + s_rank
    def crit_avoid_calc(self):
        return self.stats.lck + self.find_supports()
    def crit_accuracy_calc(self):
        # between 0 and 100
        # crit rate - crit evade
        pass
    def damage_calc(self, enemy):
        # must be >= 0
        # attack power - defense power
        # crit is 3x above formula
        pass

class Class:
    """Will be used to categorize units"""
    __slots__ =('terrain_cost')
    def __init__(self, terrain_cost):
        self.terrain_cost = terrain_cost
        