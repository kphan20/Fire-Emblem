from unit_info import SupportBonuses

affinity_bonuses = {
    "Fire": SupportBonuses(attack=0.5, hit_rate=2.5, avoid=2.5, crit_chance=2.5),
    "Thunder": SupportBonuses(defense=0.5, avoid=2.5, crit_chance=2.5, crit_avoid=2.5),
    "Wind": SupportBonuses(attack=0.5, hit_rate=2.5, crit_chance=2.5, crit_avoid=2.5),
    "Ice": SupportBonuses(defense=0.5, hit_rate=2.5, avoid=2.5, crit_avoid=2.5),
    "Dark": SupportBonuses(hit_rate=2.5, avoid=2.5, crit_chance=2.5, crit_avoid=2.5),
    "Light": SupportBonuses(attack=0.5, defense=0.5, hit_rate=2.5, crit_chance=2.5),
    "Anima": SupportBonuses(attack=0.5, defense=0.5, avoid=2.5, crit_avoid=2.5),
}


def get_affinity_bonus(aff1, aff2):
    return affinity_bonuses[aff1] + affinity_bonuses[aff2]
