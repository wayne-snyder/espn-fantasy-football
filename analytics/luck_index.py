"""
Luck index: the classic "all-play" method. Each week, imagine every
team played every other team instead of just their real opponent —
that gives an "all-play win rate" reflecting how good your score
actually was that week, independent of who you were matched against.

luck = actual wins - expected wins (sum of weekly all-play win rates)

Positive luck = your record is better than your scoring deserved
(favorable schedule). Negative luck = you're getting robbed by the
schedule.
"""

import pandas as pd

from db_utils import load_table, save_report


def main():

    matchups = load_table("weekly_matchups")
    teams = load_table("teams")

    weekly_rows = []

    for (season, week), group in matchups.groupby(["season", "week"]):

        group = group.reset_index(drop=True)
        n_teams = len(group)

        for _, row in group.iterrows():

            others = group[group["team_id"] != row["team_id"]]

            if others.empty:
                continue

            all_play_wins = (others["points_for"] < row["points_for"]).sum()
            all_play_ties = (others["points_for"] == row["points_for"]).sum()

            all_play_win_pct = (
                all_play_wins + 0.5 * all_play_ties
            ) / len(others)

            weekly_rows.append(
                {
                    "season": season,
                    "week": week,
                    "team_id": row["team_id"],
                    "actual_result": row["result"],
                    "points_for": row["points_for"],
                    "all_play_win_pct": round(all_play_win_pct, 3),
                }
            )

    weekly_df = pd.DataFrame(weekly_rows)

    weekly_df["actual_win_value"] = weekly_df["actual_result"].map(
        {"W": 1.0, "T": 0.5, "L": 0.0}
    )

    season_summary = (
        weekly_df.groupby(["season", "team_id"])
        .agg(
            actual_wins=("actual_win_value", "sum"),
            expected_wins=("all_play_win_pct", "sum"),
            weeks=("week", "count"),
        )
        .reset_index()
    )

    season_summary["luck"] = (
        season_summary["actual_wins"] - season_summary["expected_wins"]
    ).round(2)
    season_summary["expected_wins"] = season_summary["expected_wins"].round(2)

    season_summary = season_summary.merge(
        teams[["season", "team_id", "team_name"]],
        on=["season", "team_id"],
        how="left",
    )

    season_summary["luck_rank"] = season_summary.groupby("season")[
        "luck"
    ].rank(ascending=False, method="min")

    out = season_summary[
        [
            "season",
            "luck_rank",
            "team_name",
            "actual_wins",
            "expected_wins",
            "luck",
            "weeks",
        ]
    ].sort_values(["season", "luck_rank"])

    print("Luck index (season summary)")
    save_report(out, "luck_index.csv")

    return out


if __name__ == "__main__":
    main()
