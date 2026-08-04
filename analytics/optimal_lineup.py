"""
Optimal lineup comparisons: for every team-week, which bench player(s)
outscored a starter at an eligible position — i.e. exactly what you'd
change if you could redo that week's lineup with hindsight.

Note: this checks each starter slot independently, so the same bench
player can appear as the "best alternative" for more than one slot if
they were eligible for both. That's a real signal (that bench spot was
underused everywhere), but you'd only actually swap them into one slot
— use lineup_efficiency.py's optimal_points for the true single best
lineup total.
"""

import pandas as pd

from db_utils import load_table, save_report
from lineup_utils import SLOT_ELIGIBLE_POSITIONS, compute_optimal_lineup


def main():

    lineups = load_table("weekly_lineups")
    lineups["is_starter"] = lineups["is_starter"].astype(bool)
    teams = load_table("teams")

    misses = []

    for (season, team_id, week), group in lineups.groupby(
        ["season", "team_id", "week"]
    ):

        starters = group[group["is_starter"]]
        bench = group[~group["is_starter"]]

        for _, starter in starters.iterrows():

            eligible = SLOT_ELIGIBLE_POSITIONS.get(starter["lineup_slot_id"])

            bench_candidates = bench[
                bench["position"].isin(eligible) if eligible else True
            ]

            if bench_candidates.empty:
                continue

            best_bench = bench_candidates.loc[
                bench_candidates["points"].idxmax()
            ]

            if (
                best_bench["points"] is not None
                and starter["points"] is not None
                and best_bench["points"] > starter["points"]
            ):
                misses.append(
                    {
                        "season": season,
                        "team_id": team_id,
                        "week": week,
                        "slot": starter["lineup_slot"],
                        "starter_name": starter["player_name"],
                        "starter_points": starter["points"],
                        "bench_alternative": best_bench["player_name"],
                        "bench_points": best_bench["points"],
                        "points_left_on_bench": round(
                            best_bench["points"] - starter["points"], 2
                        ),
                    }
                )

    misses_df = pd.DataFrame(misses)

    if not misses_df.empty:
        misses_df = misses_df.merge(
            teams[["season", "team_id", "team_name"]],
            on=["season", "team_id"],
            how="left",
        )
        misses_df = misses_df.sort_values(
            "points_left_on_bench", ascending=False
        )

    print("Optimal lineup comparisons (biggest missed-start moments)")
    save_report(misses_df, "optimal_lineup_misses.csv")

    return misses_df


if __name__ == "__main__":
    main()
