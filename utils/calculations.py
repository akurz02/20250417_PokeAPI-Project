"""Stat calculation utilities for Pokémon Analytics."""

import math

from utils.constants import NATURE_MODIFIERS


def calculate_stat(base_stat, level, iv=31, ev=0, nature_modifier=1.0, is_hp=False):
    """Calculate a single Pokémon stat."""

    stat_value = math.floor(
        ((2 * base_stat + iv + (ev // 4)) * level) / 100
    )

    if is_hp:
        return stat_value + level + 10

    stat_value += 5
    return math.floor(stat_value * nature_modifier)


def calculate_stats(pokemon_data, level, ivs=None, evs=None, nature="Hardy"):
    """Calculate all Pokémon stats for a given level, IVs, EVs, and nature."""

    ivs = ivs or {}
    evs = evs or {}

    modifiers = NATURE_MODIFIERS.get(nature, {})

    calculated_stats = {}

    for stat in pokemon_data["stats"]:
        stat_name = stat["stat"]["name"]
        base_stat = stat["base_stat"]

        iv = ivs.get(stat_name, 31)
        ev = evs.get(stat_name, 0)

        nature_modifier = modifiers.get(stat_name, 1.0)

        calculated_stats[stat_name] = calculate_stat(
            base_stat=base_stat,
            level=level,
            iv=iv,
            ev=ev,
            nature_modifier=nature_modifier,
            is_hp=(stat_name == "hp"),
        )

    return calculated_stats


def calculate_level_projection(pokemon_data, level):
    """Calculate projected stats using 31 IVs, 0 EVs, and a neutral nature."""

    return calculate_stats(
        pokemon_data=pokemon_data,
        level=level,
        ivs={},
        evs={},
        nature="Hardy",
    )