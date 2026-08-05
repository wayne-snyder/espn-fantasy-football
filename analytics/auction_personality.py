"""
Creates career auction personality profiles.

Uses manager_id instead of fantasy team names.

Outputs:
- Spending style
- Aggression
- Patience
- Stars/Scrubs tendency
- Market impact
- Archetype
- Draft recommendations
"""

from db_utils import load_table, save_report
import pandas as pd


def calculate_archetype(row):

    aggression = row["avg_aggression"]
    patience = row["avg_patience"]
    stars = row["avg_stars_scrubs"]


    if aggression >= 70 and patience < 40:
        return "The Shark"

    if stars >= 80 and aggression >= 50:
        return "The Whale"

    if patience >= 75:
        return "The Sniper"

    if aggression < 35:
        return "The Value Hunter"

    return "Balanced"


def draft_strategy(archetype):

    strategies = {

        "The Shark":
            "Avoid bidding wars. Let them spend premium dollars.",

        "The Whale":
            "Allow elite purchases. Attack value afterward.",

        "The Sniper":
            "Do not leave bargains uncontested late.",

        "The Value Hunter":
            "Force them to spend by nominating their targets.",

        "Balanced":
            "Use normal auction tactics."
    }

    return strategies.get(
        archetype,
        ""
    )


def main():

    picks = load_table(
        "auction_picks_enriched"
    )


    # Total spending
    manager_season = (
        picks.groupby(
            [
                "manager_id",
                "season",
                "team_name"
            ]
        )
        .agg(
            total_spend=(
                "bid_amount",
                "sum"
            ),

            avg_bid=(
                "bid_amount",
                "mean"
            ),

            max_bid=(
                "bid_amount",
                "max"
            ),

            players_bought=(
                "player_id",
                "count"
            )
        )
        .reset_index()
    )


    # Spending percentage
    manager_season[
        "spend_share"
    ] = (
        manager_season[
            "total_spend"
        ]
        /
        200
        *
        100
    )


    # Early spending
    early = (
        picks[
            picks["pick_number"] <= 40
        ]
        .groupby(
            [
                "manager_id",
                "season"
            ]
        )["bid_amount"]
        .sum()
    )


    manager_season["early_spending_pct"] = (
        manager_season.apply(
            lambda x:
            early.get(
                (
                    x.manager_id,
                    x.season
                ),
                0
            )
            /
            x.total_spend
            *
            100,
            axis=1
        )
    )


    # Career profile

    career = (
        manager_season.groupby(
            "manager_id"
        )
        .agg(

            seasons=(
                "season",
                "nunique"
            ),

            team_names=(
                "team_name",
                lambda x:
                    ", ".join(
                        sorted(set(x))
                    )
            ),

            avg_spend=(
                "total_spend",
                "mean"
            ),

            avg_bid=(
                "avg_bid",
                "mean"
            ),

            avg_max_bid=(
                "max_bid",
                "mean"
            ),

            avg_early_spending=(
                "early_spending_pct",
                "mean"
            )
        )
        .reset_index()
    )


    # Personality scoring

    career["avg_aggression"] = (
        career["avg_max_bid"]
        /
        career["avg_max_bid"].max()
        *
        100
    )


    career["avg_patience"] = (
        100 -
        career["avg_early_spending"]
    )


    career["avg_stars_scrubs"] = (
        career["avg_max_bid"]
        /
        career["avg_bid"]
        *
        10
    ).clip(
        0,
        100
    )


    career["archetype"] = career.apply(
        calculate_archetype,
        axis=1
    )


    career["draft_strategy"] = (
        career["archetype"]
        .apply(
            draft_strategy
        )
    )


    career = career.round(1)


    save_report(
        career,
        "manager_personality_career.csv"
    )


    print(career)


if __name__ == "__main__":
    main()