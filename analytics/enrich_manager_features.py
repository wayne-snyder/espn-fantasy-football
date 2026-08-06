"""
Builds manager-level behavioral features from auction_features.

Feature aggregation only.
"""

import pandas as pd

from db_utils import load_table, save_report, save_table


def calculate_manager_features(df):

    results = []

    for manager_id, manager in df.groupby("manager_id"):

        manager = manager.copy()

        total_players = len(manager)

        seasons = sorted(
            manager["season"].unique()
        )

        total_spend = manager["bid_amount"].sum()


        # -------------------------------
        # Spending
        # -------------------------------

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


        # -------------------------------
        # Aggression
        # -------------------------------

        aggressive = (
            (manager["league_price_percentile"] >= .75)
            |
            (manager["is_elite_purchase"])
        )

        aggression = (
            aggressive.sum()
            /
            total_players
            *
            100
        )


        # -------------------------------
        # Patience
        # -------------------------------

        early = manager[
            manager["purchase_number"] <= 5
        ]

        early_spend_pct = (
            early["bid_amount"].sum()
            /
            total_spend
            *
            100
            if total_spend
            else 0
        )

        patience = 100 - early_spend_pct


        # -------------------------------
        # Stars & Scrubs
        # -------------------------------

        stars_scrubs = []

        for _, season_df in manager.groupby("season"):

            season_total = (
                season_df["bid_amount"]
                .sum()
            )

            top_two = (
                season_df
                .nlargest(
                    2,
                    "bid_amount"
                )["bid_amount"]
                .sum()
            )

            if season_total:
                stars_scrubs.append(
                    top_two /
                    season_total *
                    100
                )


        avg_stars_scrubs = (
            sum(stars_scrubs) /
            len(stars_scrubs)
            if stars_scrubs
            else 0
        )


        # -------------------------------
        # New features
        # -------------------------------

        elite_rate = (
            manager["is_elite_purchase"]
            .mean()
            *
            100
        )


        value_rate = (
            manager["is_value_purchase"]
            .mean()
            *
            100
        )


        position_spend = (
            manager
            .groupby("position")
            ["bid_amount"]
            .sum()
        )


        top_position_pct = (
            position_spend.max()
            /
            total_spend
            *
            100
            if total_spend
            else 0
        )


        if avg_stars_scrubs >= 55:
            roster_style = "Stars & Scrubs"

        elif top_position_pct >= 45:
            roster_style = "Position Concentration"

        elif avg_bid < 12:
            roster_style = "Depth Builder"

        else:
            roster_style = "Balanced"


        favorite_positions = ", ".join(
            position_spend
            .sort_values(
                ascending=False
            )
            .head(3)
            .index
            .tolist()
        )


        results.append({

            "manager_id":
                manager_id,

            "seasons_active":
                len(seasons),

            "first_season":
                min(seasons),

            "last_season":
                max(seasons),

            "avg_spend":
                round(avg_spend,2),

            "avg_bid":
                round(avg_bid,2),

            "avg_max_bid":
                round(avg_max_bid,2),

            "avg_aggression":
                round(aggression,1),

            "avg_patience":
                round(patience,1),

            "avg_stars_scrubs":
                round(avg_stars_scrubs,1),

            "elite_purchase_rate":
                round(elite_rate,1),

            "value_purchase_rate":
                round(value_rate,1),

            "position_concentration":
                round(top_position_pct,1),

            "roster_style":
                roster_style,

            "favorite_positions":
                favorite_positions
        })


    return pd.DataFrame(results)



def main():

    auction = load_table(
        "auction_features"
    )


    features = calculate_manager_features(
        auction
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