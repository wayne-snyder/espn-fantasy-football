"""
Draft value vs. auction cost: for every drafted player, how many
fantasy points did they score that season per dollar spent? Ranked
within each season so you can see your league's best/worst bargains
and busts historically — useful for setting price tiers going into
your auction.
"""

from db_utils import load_table, save_report


def main():

    picks = load_table("auction_picks")
    lineups = load_table("weekly_lineups")

    season_points = (
        lineups.groupby(["season", "player_id"])["points"]
        .sum()
        .reset_index()
        .rename(columns={"points": "season_points"})
    )

    df = picks.merge(season_points, on=["season", "player_id"], how="left")

    df["season_points"] = df["season_points"].fillna(0)

    # Avoid divide-by-zero for $0 keeper/bid entries
    df["points_per_dollar"] = df.apply(
        lambda r: (r["season_points"] / r["bid_amount"])
        if r["bid_amount"] and r["bid_amount"] > 0
        else None,
        axis=1,
    )

    df["value_rank"] = df.groupby("season")["points_per_dollar"].rank(
        ascending=False, method="min"
    )

    df = df.sort_values(["season", "value_rank"])

    out = df[
        [
            "season",
            "player_name",
            "position",
            "fantasy_team",
            "bid_amount",
            "season_points",
            "points_per_dollar",
            "value_rank",
            "keeper",
        ]
    ]

    print("Draft value vs. auction cost")
    save_report(out, "draft_value.csv")

    return out


if __name__ == "__main__":
    main()
