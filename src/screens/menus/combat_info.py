from typing import Tuple
import pyglet
from pyglet.graphics import Batch, Group
from game import resources
from game.unit import Character
from game.game_formulas import (
    attack_power,
    defense_power,
    accuracy_calc,
    crit_accuracy_calc,
)

hp_y_offset = 360
mt_y_offset = 290
hit_y_offest = 230
crit_y_offset = 160
enemy_x_offset = 20
current_x_offset = 200


class CombatMenu(pyglet.sprite.Sprite):
    def __init__(
        self, batch: Batch, menu_group: Group, text_group: Group, screen_width: int
    ):
        super().__init__(resources.combat_menu, batch=batch, group=menu_group)

        self.scale = 4
        x_pos = screen_width - self.width - 25
        y_pos = 135
        self.position = (x_pos, y_pos)

        self.hp = pyglet.text.Label(batch=batch, group=text_group)
        self.mt = pyglet.text.Label(batch=batch, group=text_group)
        self.hit = pyglet.text.Label(batch=batch, group=text_group)
        self.crit = pyglet.text.Label(batch=batch, group=text_group)

        self.enemy_hp = pyglet.text.Label(
            x=x_pos + enemy_x_offset,
            y=y_pos + hp_y_offset,
            batch=batch,
            group=text_group,
        )
        self.current_hp = pyglet.text.Label(
            x=x_pos + current_x_offset,
            y=y_pos + hp_y_offset,
            batch=batch,
            group=text_group,
        )
        self.enemy_mt = pyglet.text.Label(
            x=x_pos + enemy_x_offset,
            y=y_pos + mt_y_offset,
            batch=batch,
            group=text_group,
        )
        self.current_mt = pyglet.text.Label(
            x=x_pos + current_x_offset,
            y=y_pos + mt_y_offset,
            batch=batch,
            group=text_group,
        )
        self.enemy_hit = pyglet.text.Label(
            x=x_pos + enemy_x_offset,
            y=y_pos + hit_y_offest,
            batch=batch,
            group=text_group,
        )
        self.current_hit = pyglet.text.Label(
            x=x_pos + current_x_offset,
            y=y_pos + hit_y_offest,
            batch=batch,
            group=text_group,
        )
        self.enemy_crit = pyglet.text.Label(
            x=x_pos + enemy_x_offset,
            y=y_pos + crit_y_offset,
            batch=batch,
            group=text_group,
        )
        self.current_crit = pyglet.text.Label(
            x=x_pos + current_x_offset,
            y=y_pos + crit_y_offset,
            batch=batch,
            group=text_group,
        )

        self.text = [
            self.hp,
            self.enemy_hp,
            self.current_hp,
            self.mt,
            self.enemy_mt,
            self.current_mt,
            self.hit,
            self.enemy_hit,
            self.current_hit,
            self.crit,
            self.enemy_crit,
            self.current_crit,
        ]

    def set_batch(self, batch: Batch):
        self.batch = batch

        for text in self.text:
            text.batch = batch

    def set_text(
        self,
        curr_hp,
        curr_mt,
        curr_hit,
        curr_crit,
        enemy_hp,
        enemy_mt=None,
        enemy_hit=None,
        enemy_crit=None,
    ):
        self.current_hp.text = curr_hp
        self.current_mt.text = curr_mt
        self.current_hit.text = curr_hit
        self.current_crit.text = curr_crit
        self.enemy_hp.text = enemy_hp
        self.enemy_mt.text = enemy_mt if enemy_mt is not None else "- -"
        self.enemy_hit.text = enemy_hit if enemy_hit is not None else "- -"
        self.enemy_crit.text = enemy_crit if enemy_crit is not None else "- -"

    def get_info(self, attacking_unit: Character, attacked_unit: Character) -> Tuple:
        curr_mt = attack_power(attacking_unit, attacked_unit) - defense_power(
            attacked_unit
        )
        curr_hit = accuracy_calc(attacking_unit, attacked_unit, 0)
        curr_crit = crit_accuracy_calc(attacking_unit, attacked_unit)
        return str(curr_mt), str(curr_hit), str(curr_crit)

    def update_text_with_characters(
        self, attacking_unit: Character, attacked_unit: Character
    ):
        self.set_text(
            str(attacking_unit.current_hp),
            *self.get_info(attacking_unit, attacked_unit),
            str(attacked_unit.current_hp),
            *self.get_info(attacked_unit, attacking_unit),
        )
