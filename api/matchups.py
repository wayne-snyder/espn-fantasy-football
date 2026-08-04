from api.constants import BENCH_SLOTS, LINEUP_SLOT_MAP, PLAYER_POSITION_MAP


def get_boxscore(client, season, league_id, scoring_period_id):
    return client.get_boxscore(season, league_id, scoring_period_id)


def get_final_week(league_data, fallback=17):
    """
    ESPN reports the last completed fantasy week (regular season +
    playoffs) as status.finalScoringPeriod once a season has wrapped.
    Falls back to a fixed guess for in-progress/older seasons where
    that field isn't present.
    """

    return (
        league_data.get("status", {}).get("finalScoringPeriod")
        or fallback
    )


def extract_weekly_lineups(boxscore_data, season, week):
    """
    Flattens one week's box score into one row per rostered player:
    who started, who sat, and how many points they scored that week.
    """

    rows = []

    matchups = boxscore_data.get("schedule", [])

    for matchup in matchups:

        if matchup.get("matchupPeriodId") != week:
            continue

        for side in ("home", "away"):

            team_side = matchup.get(side)

            if not team_side:
                # bye week (odd number of teams) has no "away" side
                continue

            team_id = team_side.get("teamId")

            entries = team_side.get(
                "rosterForCurrentScoringPeriod", {}
            ).get("entries", [])

            for entry in entries:

                player = entry.get("playerPoolEntry", {}).get("player", {})

                slot_id = entry.get("lineupSlotId")
                position_id = player.get("defaultPositionId")

                rows.append(
                    {
                        "season": season,
                        "week": week,
                        "team_id": team_id,
                        "player_id": player.get("id"),
                        "player_name": player.get("fullName"),
                        "position": PLAYER_POSITION_MAP.get(
                            position_id, position_id
                        ),
                        "lineup_slot_id": slot_id,
                        "lineup_slot": LINEUP_SLOT_MAP.get(slot_id, slot_id),
                        "is_starter": slot_id not in BENCH_SLOTS,
                        "points": entry.get("playerPoolEntry", {}).get(
                            "appliedStatTotal"
                        ),
                    }
                )

    return rows


def extract_matchup_results(boxscore_data, season, week):
    """
    One row per team per week: their score, their opponent's score,
    and the result. Used for power rankings and luck index.
    """

    rows = []

    matchups = boxscore_data.get("schedule", [])

    for matchup in matchups:

        if matchup.get("matchupPeriodId") != week:
            continue

        home = matchup.get("home")
        away = matchup.get("away")

        if not home or not away:
            # bye week — no matchup to score
            continue

        pairs = [(home, away), (away, home)]

        for team_side, opp_side in pairs:

            team_score = team_side.get("totalPoints")
            opp_score = opp_side.get("totalPoints")

            if team_score is None or opp_score is None:
                result = None
            elif team_score > opp_score:
                result = "W"
            elif team_score < opp_score:
                result = "L"
            else:
                result = "T"

            rows.append(
                {
                    "season": season,
                    "week": week,
                    "team_id": team_side.get("teamId"),
                    "opponent_team_id": opp_side.get("teamId"),
                    "points_for": team_score,
                    "points_against": opp_score,
                    "result": result,
                }
            )

    return rows
