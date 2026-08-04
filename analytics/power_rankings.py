"""
Power rankings: a composite score per team per week, blending
season-to-date win rate, season-to-date scoring average, and recent
form (avg points over the last 3 weeks). Each component is normalized
0-1 within that week's field before being weighted, so the score isn't
dominated by whichever metric happens to have the largest raw scale.

Weights (40% record, 30% scoring average, 30% recent form) are a
reasonable default — adjust WEIGHTS below to match how your league
likes to argue about power rankings.
"""

import pandas as pd

from db_utils import load_table, save_report

WEIGHTS = {"win_pct": 0.4, "avg_points_for": 0.3, "recent_form": 0.3}


def normalize(series):
    lo, hi = series.min(), series.max()
    if hi == lo:
        return series.apply(lambda _: 0.5)
    return (series - lo) / (hi - lo)


def main():

    matchups = load_table("weekly_matchups")
    teams = load_table("teams")

    matchups = matchups.sort_values(["season", "team_id", "week"])

    rows = []

    for (season, team_id), group in matchups.groupby(["season", "team_id"]):

        group = group.sort_values("week").reset_index(drop=True)

        for i in range(len(group)):

            so_far = group.iloc[: i + 1]
            recent = group.iloc[max(0, i - 2) : i + 1]  # last 3 weeks

            wins = (so_far["result"] == "W").sum()
            games = so_far["result"].notna().sum()

            rows.append(
                {
                    "season": season,
                    "team_id": team_id,
                    "week": group.iloc[i]["week"],
                    "win_pct": wins / games if games else None,
                    "avg_points_for": so_far["points_for"].mean(),
                    "recent_form": recent["points_for"].mean(),
                }
            )

    df = pd.DataFrame(rows)

    # Normalize each metric within its own (season, week) so scores are
    # comparable across a field of teams rather than across raw units
    for col in ["win_pct", "avg_points_for", "recent_form"]:
        df[f"{col}_norm"] = df.groupby(["season", "week"])[col].transform(
            normalize
        )

    df["power_score"] = (
        df["win_pct_norm"] * WEIGHTS["win_pct"]
        + df["avg_points_for_norm"] * WEIGHTS["avg_points_for"]
        + df["recent_form_norm"] * WEIGHTS["recent_form"]
    ) * 100

    df["power_score"] = df["power_score"].round(1)

    df["power_rank"] = df.groupby(["season", "week"])["power_score"].rank(
        ascending=False, method="min"
    )

    df = df.merge(
        teams[["season", "team_id", "team_name"]],
        on=["season", "team_id"],
        how="left",
    )

    out = df[
        [
            "season",
            "week",
            "power_rank",
            "team_name",
            "power_score",
            "win_pct",
            "avg_points_for",
            "recent_form",
        ]
    ].sort_values(["season", "week", "power_rank"])

    print("Power rankings (weekly)")
    save_report(out, "power_rankings.csv")

    latest = out.loc[out.groupby("season")["week"].transform("max") == out["week"]]
    print("Power rankings (latest week per season)")
    save_report(latest, "power_rankings_latest.csv")

    return out


if __name__ == "__main__":
    main()
