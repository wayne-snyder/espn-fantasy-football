"""
Position spending: how auction budgets get allocated across positions,
per season and averaged across all seasons. Useful for setting your
own budget targets before the auction (e.g. "RBs typically eat 40% of
the room's total spend").
"""

from db_utils import load_table, save_report


def main():

    picks = load_table("auction_picks")
    settings = load_table("league_settings")

    by_season_position = (
        picks.groupby(["season", "position"])
        .agg(
            total_spend=("bid_amount", "sum"),
            avg_bid=("bid_amount", "mean"),
            players_bought=("player_id", "count"),
        )
        .reset_index()
    )

    season_totals = picks.groupby("season")["bid_amount"].sum().rename(
        "season_total_spend"
    )

    by_season_position = by_season_position.merge(
        season_totals, on="season", how="left"
    )

    by_season_position["pct_of_total_spend"] = (
        by_season_position["total_spend"]
        / by_season_position["season_total_spend"]
        * 100
    ).round(1)

    by_season_position["avg_bid"] = by_season_position["avg_bid"].round(2)

    by_season_position = by_season_position.sort_values(
        ["season", "total_spend"], ascending=[True, False]
    )

    print("Position spending (by season)")
    save_report(
        by_season_position.drop(columns=["season_total_spend"]),
        "position_spending_by_season.csv",
    )

    # Averaged across all seasons — the "budget cheat sheet" view
    overall = (
        by_season_position.groupby("position")
        .agg(
            avg_pct_of_budget=("pct_of_total_spend", "mean"),
            avg_bid=("avg_bid", "mean"),
            avg_players_bought_per_season=("players_bought", "mean"),
        )
        .round(1)
        .reset_index()
        .sort_values("avg_pct_of_budget", ascending=False)
    )

    print("Position spending (all-time average — draft cheat sheet)")
    save_report(overall, "position_spending_overall.csv")

    return by_season_position, overall


if __name__ == "__main__":
    main()
