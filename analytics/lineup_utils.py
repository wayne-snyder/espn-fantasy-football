"""
Shared logic for figuring out the best possible lineup a team could
have started in a given week, given their full roster (starters +
bench) for that week.

This is a greedy approximation, not a guaranteed-optimal solver: it
fills the most position-restrictive slots (QB, RB, WR, TE, K, D/ST)
first, then flexible slots (FLEX, superflex) last from whoever's left.
That covers standard ESPN lineups correctly; it can be slightly off
only in leagues with unusual/multiple flex-of-flex slot structures.
"""

# lineup_slot_id -> set of player positions eligible to fill it
SLOT_ELIGIBLE_POSITIONS = {
    0: {"QB"},
    2: {"RB"},
    4: {"WR"},
    6: {"TE"},
    16: {"D/ST"},
    17: {"K"},
    23: {"RB", "WR", "TE"},  # FLEX
    7: {"QB", "RB", "WR", "TE"},  # OP / superflex
}


def compute_optimal_lineup(required_slot_ids, roster):
    """
    required_slot_ids: list of lineup_slot_id values that need filling
        (typically the slots the team actually started that week).
    roster: list of dicts with player_id, player_name, position, points
        — the team's FULL roster for that week (starters + bench).

    Returns (optimal_total_points, assignments) where assignments is a
    list of {slot, player_id, player_name, position, points}.
    """

    # Most restrictive slots (fewest eligible positions) filled first
    ordered_slots = sorted(
        required_slot_ids,
        key=lambda s: len(SLOT_ELIGIBLE_POSITIONS.get(s, {"?", "??"})),
    )

    used_player_ids = set()
    assignments = []
    total = 0.0

    for slot in ordered_slots:

        eligible = SLOT_ELIGIBLE_POSITIONS.get(slot)

        candidates = [
            p
            for p in roster
            if p["player_id"] not in used_player_ids
            and p.get("points") is not None
            and (eligible is None or p.get("position") in eligible)
        ]

        if not candidates:
            continue

        best = max(candidates, key=lambda p: p["points"])

        used_player_ids.add(best["player_id"])
        total += best["points"]

        assignments.append({"slot": slot, **best})

    return total, assignments
