from typing import NamedTuple


def add_tuples(first, second):
    if first.__class__ != second.__class__:
        raise ValueError("Unmatching tuple type addition")

    return first.__class__(*(field1 + field2 for field1, field2 in zip(first, second)))


# consider switching to dataclass
class Stats(NamedTuple):
    """Can double as growths object"""

    hp: int = 1
    str: int = 0
    skl: int = 0
    spd: int = 0
    lck: int = 0
    def_: int = 0
    res: int = 0
    con: int = 0
    mov: int = 0
    # __slots__=('level', 'hp', 'str', 'skl', 'spd', 'lck', 'def_', 'res', 'con', 'mov')
    # def __init__(self, hp, str, skl, spd, lck, def_, res, con, mov):
    #     super().__init__(hp, str, skl, spd, lck, def_, res, con, mov)

    def __add__(self, other_stats):
        return add_tuples(self, other_stats)


class SupportBonuses(NamedTuple):
    attack: float = 0
    defense: float = 0
    hit_rate: float = 0
    avoid: float = 0
    crit_chance: float = 0
    crit_avoid: float = 0

    def __add__(self, other_bonuses):
        return add_tuples(self, other_bonuses)

    def __mul__(self, scalar: int):
        return self.__class__(*(field1 * scalar for field1 in self))


class Class:
    """Will be used to categorize units"""

    # __slots__ = ("terrain_cost", "mov", "con", "class_crit", "classname")

    def __init__(
        self, terrain_cost, mov, con, class_crit, class_attributes={}, classname=""
    ):
        self.terrain_cost = terrain_cost
        self.mov = mov
        self.con = con
        self.class_crit = class_crit
        self.classname = classname

        # maybe extract this out to a class attributes class
        self.class_attributes = class_attributes

    def set_classname(self, name):
        self.classname = name

    def calc_aid(self):
        """Used to calculate the aid based on mount and con

        Returns:
            int: Aid value used for rescue calculation
        """
        return self.con - 1
