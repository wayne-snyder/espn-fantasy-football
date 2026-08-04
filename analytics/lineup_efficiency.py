"""
Lineup efficiency: for every team-week, how many of the points sitting
on their full roster did they actually capture by starting the right
players? efficiency_pct = actual starting points / best possible
lineup from that week's full roster.
"""

import pandas as pd

from db_utils import load_table, save_report
from lineup_utils import compute_optimal_lineup


def main():

    lineups = load_table("weekly_lineups")
    lineups["is_starter"] = lineups["is_starter"].astype(bool)
    teams = load_table("teams")

    weekly_rows = []

    for (season, team_id, week), group in lineups.groupby(
        ["season", "team_id", "week"]
    ):

        actual_points = group.loc[group["is_starter"], "points"].sum()

        required_slots = group.loc[
            group["is_starter"], "lineup_slot_id"
        ].tolist()

        roster = group[
            ["player_id", "player_name", "position", "points"]
        ].to_dict("records")

        optimal_points, _ = compute_optimal_lineup(required_slots, roster)

        efficiency = (
            actual_points / optimal_points if optimal_points else None
        )

        weekly_rows.append(
            {
                "season": season,
                "team_id": team_id,
                "week": week,
                "actual_points": actual_points,
                "optimal_points": optimal_points,
                "points_left_on_bench": optimal_points - actual_points,
                "efficiency_pct": round(efficiency * 100, 1)
                if efficiency is not None
                else None,
            }
        )

    weekly_df = pd.DataFrame(weekly_rows)
    weekly_df = weekly_df.merge(
        teams[["season", "team_id", "team_name"]],
        on=["season", "team_id"],
        how="left",
    )

    season_summary = (
        weekly_df.groupby(["season", "team_id", "team_name"])
        .agg(
            avg_efficiency_pct=("efficiency_pct", "mean"),
            total_points_left_on_bench=("points_left_on_bench", "sum"),
            weeks=("week", "count"),
        )
        .reset_index()
        .sort_values(["season", "avg_efficiency_pct"], ascending=[True, False])
    )
    season_summary["avg_efficiency_pct"] = season_summary[
        "avg_efficiency_pct"
    ].round(1)

    print("Lineup efficiency (weekly detail)")
    save_report(
        weekly_df.sort_values(["season", "week", "team_id"]),
        "lineup_efficiency_weekly.csv",
    )

    print("Lineup efficiency (season summary)")
    save_report(season_summary, "lineup_efficiency_season.csv")

    return weekly_df, season_summary


if __name__ == "__main__":
    main()
