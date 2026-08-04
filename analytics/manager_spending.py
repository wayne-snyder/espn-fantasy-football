"""
Manager spending trends: how each fantasy team has spent their auction
budget across seasons — total spend, average bid, biggest single bid,
and spend as a percent of that season's budget.
"""

from db_utils import load_table, save_report


def main():

    picks = load_table("auction_picks")
    settings = load_table("league_settings")

    by_team_season = (
        picks.groupby(["season", "fantasy_team_id", "fantasy_team"])
        .agg(
            total_spend=("bid_amount", "sum"),
            avg_bid=("bid_amount", "mean"),
            max_bid=("bid_amount", "max"),
            players_bought=("player_id", "count"),
        )
        .reset_index()
    )

    by_team_season = by_team_season.merge(
        settings[["season", "auction_budget"]], on="season", how="left"
    )

    by_team_season["pct_of_budget_spent"] = (
        by_team_season["total_spend"] / by_team_season["auction_budget"] * 100
    ).round(1)

    by_team_season["avg_bid"] = by_team_season["avg_bid"].round(2)

    by_team_season = by_team_season.sort_values(
        ["season", "total_spend"], ascending=[True, False]
    )

    print("Manager spending trends (by season)")
    save_report(by_team_season, "manager_spending_by_season.csv")

    # Multi-season trend per manager
    trend = (
        by_team_season.groupby("fantasy_team")
        .agg(
            seasons=("season", "count"),
            avg_spend=("total_spend", "mean"),
            avg_pct_of_budget=("pct_of_budget_spent", "mean"),
            avg_bid=("avg_bid", "mean"),
        )
        .round(1)
        .reset_index()
        .sort_values("avg_spend", ascending=False)
    )

    print("Manager spending trends (career average)")
    save_report(trend, "manager_spending_career.csv")

    return by_team_season, trend


if __name__ == "__main__":
    main()
