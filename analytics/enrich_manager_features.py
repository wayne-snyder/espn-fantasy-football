"""
Builds manager-level behavioral features from auction_features.

This module is responsible only for feature aggregation.
Analytics and reports should consume manager_features.
"""

import pandas as pd

from db_utils import load_table, save_report, save_table


def calculate_manager_features(df):
    """
    Creates one row per manager with historical auction behavior.
    """

    results = []

    for manager_id, manager in df.groupby("manager_id"):

        manager = manager.copy()

        # -----------------------------------
        # Seasons
        # -----------------------------------

        seasons = sorted(
            manager["season"].unique().tolist()
        )

        total_players = len(manager)

        # -----------------------------------
        # Spending behavior
        # -----------------------------------

        season_spend = (
            manager
            .groupby("season")["bid_amount"]
            .sum()
        )

        avg_spend = season_spend.mean()

        avg_bid = manager["bid_amount"].mean()

        avg_max_bid = (
            manager
            .groupby("season")["bid_amount"]
            .max()
            .mean()
        )

        # -----------------------------------
        # Aggression
        # -----------------------------------

        aggressive_mask = (
            (
                manager["league_price_percentile"] >= 0.75
            )
            |
            (
                manager["is_elite_purchase"]
            )
        )

        aggressive_purchases = aggressive_mask.sum()

        aggression = (
            aggressive_purchases
            / total_players
            * 100
            if total_players > 0
            else 0
        )

        # -----------------------------------
        # Patience / Spending Timing
        # -----------------------------------

        early_draft = manager[
            manager["purchase_number"] <= 5
        ]

        total_spend = manager["bid_amount"].sum()

        early_spend = (
            early_draft["bid_amount"]
            .sum()
        )

        early_spending_pct = (
            early_spend
            / total_spend
            * 100
            if total_spend > 0
            else 0
        )

        # Higher = waits longer to spend

        patience = (
            100
            - early_spending_pct
        )

        # -----------------------------------
        # Stars and Scrubs
        # -----------------------------------

        stars_scrubs_scores = []

        for season, draft in manager.groupby("season"):

            draft = draft.sort_values(
                "bid_amount",
                ascending=False
            )

            season_total = (
                draft["bid_amount"]
                .sum()
            )

            if season_total == 0:
                continue

            top_two = (
                draft
                .head(2)["bid_amount"]
                .sum()
            )

            stars_scrubs_scores.append(
                top_two
                / season_total
                * 100
            )

        avg_stars_scrubs = (
            sum(stars_scrubs_scores)
            / len(stars_scrubs_scores)
            if stars_scrubs_scores
            else 0
        )

        # -----------------------------------
        # Favorite positions
        # -----------------------------------

        positions = (
            manager
            .groupby("position")["bid_amount"]
            .sum()
            .sort_values(
                ascending=False
            )
        )

        favorite_positions = ", ".join(
            positions
            .head(3)
            .index
            .tolist()
        )

        # -----------------------------------
        # Save
        # -----------------------------------

        results.append(

            {
                "manager_id":
                    manager_id,

                "seasons_active":
                    len(seasons),

                "first_season":
                    min(seasons),

                "last_season":
                    max(seasons),

                "avg_spend":
                    round(avg_spend, 2),

                "avg_bid":
                    round(avg_bid, 2),

                "avg_max_bid":
                    round(avg_max_bid, 2),

                "avg_aggression":
                    round(aggression, 1),

                "avg_patience":
                    round(patience, 1),

                "avg_stars_scrubs":
                    round(avg_stars_scrubs, 1),

                "favorite_positions":
                    favorite_positions,
            }

        )

    return pd.DataFrame(results)


def main():

    auction = load_table(
        "auction_features"
    )

    features = calculate_manager_features(
        auction
    )

    print(
        f"Created manager_features ({len(features)} rows)"
    )

    print(
        features.head()
    )

    save_report(
        features,
        "manager_features.csv"
    )

    save_table(
        features,
        "manager_features"
    )


if __name__ == "__main__":
    main()