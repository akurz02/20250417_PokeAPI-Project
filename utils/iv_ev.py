"""IV and EV analysis utilities for Pokémon Analytics.

Generalized stat-reconstruction engine for known or unknown IVs and EVs.
"""

from utils.constants import (
    MAX_EV_PER_STAT,
    MAX_IV,
    MAX_TOTAL_EV,
    MIN_EV,
    MIN_IV,
    NATURE_MODIFIERS,
)
from utils.calculations import calculate_stat


def _ev_values():
    """Return every legal integer EV value for a stat."""
    return range(MIN_EV, MAX_EV_PER_STAT + 1)


def _validate_observed_stat(value):
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _validate_iv(value):
    return (
        isinstance(value, int)
        and not isinstance(value, bool)
        and MIN_IV <= value <= MAX_IV
    )


def _validate_ev(value):
    return (
        isinstance(value, int)
        and not isinstance(value, bool)
        and MIN_EV <= value <= MAX_EV_PER_STAT
    )


def _candidate_values(
    base_stat,
    level,
    observed_stat,
    known_iv=None,
    known_ev=None,
    nature_modifier=1.0,
    is_hp=False,
):
    """Find exact IV/EV pairs that reproduce one observed stat."""
    iv_values = [known_iv] if known_iv is not None else range(MIN_IV, MAX_IV + 1)
    ev_values = [known_ev] if known_ev is not None else _ev_values()

    candidates = []

    for iv in iv_values:
        for ev in ev_values:
            calculated = calculate_stat(
                base_stat=base_stat,
                level=level,
                iv=iv,
                ev=ev,
                nature_modifier=nature_modifier,
                is_hp=is_hp,
            )
            if calculated == observed_stat:
                candidates.append({"iv": iv, "ev": ev})

    return candidates


def find_possible_ivs(
    base_stat,
    level,
    observed_stat,
    ev=0,
    nature_modifier=1.0,
    is_hp=False,
):
    """Find IV values compatible with an observed stat when EVs are known."""
    if not _validate_observed_stat(observed_stat) or not _validate_ev(ev):
        return []

    candidates = _candidate_values(
        base_stat,
        level,
        observed_stat,
        known_ev=ev,
        nature_modifier=nature_modifier,
        is_hp=is_hp,
    )
    return [candidate["iv"] for candidate in candidates]


def find_possible_ev_spreads(
    base_stat,
    level,
    observed_stat,
    iv=None,
    nature_modifier=1.0,
    is_hp=False,
):
    """Find compatible EV ranges, grouped by IV.

    Actual integer EVs are searched because the formula uses EV // 4.
    """
    if not _validate_observed_stat(observed_stat):
        return []
    if iv is not None and not _validate_iv(iv):
        return []

    candidates = _candidate_values(
        base_stat,
        level,
        observed_stat,
        known_iv=iv,
        nature_modifier=nature_modifier,
        is_hp=is_hp,
    )

    grouped = []
    for candidate in candidates:
        current_iv = candidate["iv"]
        current_ev = candidate["ev"]

        if (
            grouped
            and grouped[-1]["iv"] == current_iv
            and current_ev == grouped[-1]["ev_max"] + 1
        ):
            grouped[-1]["ev_max"] = current_ev
        else:
            grouped.append(
                {
                    "iv": current_iv,
                    "ev_min": current_ev,
                    "ev_max": current_ev,
                }
            )

    return grouped


def _build_stat_candidates(
    pokemon_data,
    level,
    observed_stats,
    known_ivs,
    known_evs,
    nature,
):
    """Build exact compatible candidates for each observed stat."""
    modifiers = NATURE_MODIFIERS.get(nature, {})
    stat_candidates = {}

    for stat in pokemon_data["stats"]:
        stat_name = stat["stat"]["name"]

        if stat_name not in observed_stats:
            continue

        observed_stat = observed_stats[stat_name]
        if not _validate_observed_stat(observed_stat):
            stat_candidates[stat_name] = []
            continue

        known_iv = known_ivs.get(stat_name)
        known_ev = known_evs.get(stat_name)

        if known_iv is not None and not _validate_iv(known_iv):
            stat_candidates[stat_name] = []
            continue

        if known_ev is not None and not _validate_ev(known_ev):
            stat_candidates[stat_name] = []
            continue

        stat_candidates[stat_name] = _candidate_values(
            base_stat=stat["base_stat"],
            level=level,
            observed_stat=observed_stat,
            known_iv=known_iv,
            known_ev=known_ev,
            nature_modifier=modifiers.get(stat_name, 1.0),
            is_hp=(stat_name == "hp"),
        )

    return stat_candidates


def _search_builds(candidate_items, index, current_build, total_ev, results, max_results):
    """Depth-first search with pruning by the 510 total-EV limit."""
    if len(results) >= max_results:
        return

    if index == len(candidate_items):
        results.append(
            {
                "ivs": {name: data["iv"] for name, data in current_build.items()},
                "evs": {name: data["ev"] for name, data in current_build.items()},
                "total_evs": total_ev,
            }
        )
        return

    stat_name, candidates = candidate_items[index]

    for candidate in candidates:
        new_total = total_ev + candidate["ev"]
        if new_total > MAX_TOTAL_EV:
            continue

        current_build[stat_name] = candidate
        _search_builds(
            candidate_items,
            index + 1,
            current_build,
            new_total,
            results,
            max_results,
        )
        del current_build[stat_name]

        if len(results) >= max_results:
            return


def _summarize_candidates(stat_candidates):
    """Summarize possible IV and EV values for each observed stat."""
    summary = {}

    for stat_name, candidates in stat_candidates.items():
        if not candidates:
            summary[stat_name] = {
                "iv_min": None,
                "iv_max": None,
                "ev_min": None,
                "ev_max": None,
                "possible_ivs": [],
                "possible_evs": [],
            }
            continue

        ivs = sorted({candidate["iv"] for candidate in candidates})
        evs = sorted({candidate["ev"] for candidate in candidates})

        summary[stat_name] = {
            "iv_min": min(ivs),
            "iv_max": max(ivs),
            "ev_min": min(evs),
            "ev_max": max(evs),
            "possible_ivs": ivs,
            "possible_evs": evs,
        }

    return summary


def analyze_stats(
    pokemon_data,
    level,
    observed_stats,
    nature="Hardy",
    known_ivs=None,
    known_evs=None,
    max_results=500,
):
    """Reconstruct compatible IV/EV builds from observed stats.

    Known IVs, known EVs, both, either, or neither may be supplied.
    Multiple compatible builds are returned when the data is ambiguous.
    """
    known_ivs = known_ivs or {}
    known_evs = known_evs or {}

    if not isinstance(observed_stats, dict):
        return {
            "status": "no_observations",
            "solutions_found": 0,
            "stat_candidates": {},
            "stat_ranges": {},
            "builds": [],
            "truncated": False,
        }

    if not isinstance(max_results, int) or max_results < 1:
        max_results = 500

    stat_candidates = _build_stat_candidates(
        pokemon_data,
        level,
        observed_stats,
        known_ivs,
        known_evs,
        nature,
    )

    if not stat_candidates:
        return {
            "status": "no_observations",
            "solutions_found": 0,
            "stat_candidates": {},
            "stat_ranges": {},
            "builds": [],
            "truncated": False,
        }

    stat_ranges = _summarize_candidates(stat_candidates)

    if any(not candidates for candidates in stat_candidates.values()):
        return {
            "status": "no_solutions",
            "solutions_found": 0,
            "stat_candidates": stat_candidates,
            "stat_ranges": stat_ranges,
            "builds": [],
            "truncated": False,
        }

    # Search the most constrained stats first to reduce branching.
    candidate_items = sorted(
        stat_candidates.items(),
        key=lambda item: len(item[1]),
    )

    results = []
    _search_builds(
        candidate_items,
        0,
        {},
        0,
        results,
        max_results,
    )

    truncated = len(results) >= max_results

    if not results:
        status = "no_solutions"
    elif len(results) == 1 and not truncated:
        status = "unique"
    else:
        status = "multiple"

    return {
        "status": status,
        "solutions_found": len(results),
        "stat_candidates": stat_candidates,
        "stat_ranges": stat_ranges,
        "builds": results,
        "truncated": truncated,
    }


def find_matching_builds(
    pokemon_data,
    level,
    observed_stats,
    nature="Hardy",
    known_evs=None,
    known_ivs=None,
    max_results=500,
):
    """Backward-compatible wrapper around analyze_stats()."""
    analysis = analyze_stats(
        pokemon_data=pokemon_data,
        level=level,
        observed_stats=observed_stats,
        nature=nature,
        known_ivs=known_ivs,
        known_evs=known_evs,
        max_results=max_results,
    )

    builds = []
    for build in analysis["builds"]:
        flattened = {}

        for stat_name, iv in build["ivs"].items():
            ev = build["evs"][stat_name]
            flattened[stat_name] = {
                "iv": iv,
                "ev_min": ev,
                "ev_max": ev,
            }

        flattened["_total_ev_min"] = build["total_evs"]
        flattened["_total_ev_max"] = build["total_evs"]
        builds.append(flattened)

    return builds
