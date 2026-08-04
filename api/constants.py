"""
ESPN's fantasy API uses numeric IDs for player positions and lineup
slots instead of names. These mappings are reverse-engineered/community
knowledge (ESPN doesn't publish them officially) — spot-check against
your league's actual data in output/ if a report shows unexpected blanks.
"""

# player["defaultPositionId"] -> the player's real-world position
PLAYER_POSITION_MAP = {
    1: "QB",
    2: "RB",
    3: "WR",
    4: "TE",
    5: "K",
    16: "D/ST",
}

# entry["lineupSlotId"] -> the roster slot a player was placed in for a
# given week (starting lineup slot, FLEX, bench, or IR)
LINEUP_SLOT_MAP = {
    0: "QB",
    2: "RB",
    3: "RB/WR",
    4: "WR",
    5: "WR/TE",
    6: "TE",
    7: "OP",
    16: "D/ST",
    17: "K",
    20: "BE",
    21: "IR",
    23: "FLEX",
}

BENCH_SLOTS = {20, 21}
