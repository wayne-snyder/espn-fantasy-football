"""
Auction Personality Analytics

Consumes auction_features and creates manager behavior profiles.

This file should interpret behavior only.
Feature engineering belongs in analytics/core.
"""

from db_utils import load_table, save_report


def classify_archetype(row):
    """
    Classifies manager auction personality.
    """

    aggression = row["avg_aggression"]
    patience = row["avg_patience"]
    stars = row["avg_stars_scrubs"]

    if aggression >= 75 and patience < 40:
        return "The Shark"

    if patience >= 70 and aggression < 50:
        return "The Sniper"

    if stars >= 75:
        return "Stars and Scrubs"

    if stars <= 30 and patience >= 60:
        return "Value Hunter"

    return "Balanced"



def strategy_description(archetype):

    strategies = {

        "The Shark":
            "Aggressive bidder. Expect premium bids early. Avoid unnecessary bidding wars.",

        "The Sniper":
            "Patient manager. Let others spend first, attack discounts late.",

        "Stars and Scrubs":
            "Concentrates money into elite players. Exploit weak roster depth.",

        "Value Hunter":
            "Avoids premium prices. Target players after market cools.",

        "Balanced":
            "No extreme tendency. Use standard auction tactics."
    }

    return strategies.get(
        archetype,
        "Unknown"
    )



def build_personality_features(df):

    manager = (
        df.groupby(
            [
                "manager_id"
            ]
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
                    sorted(
                        set(x)
                    )
                )
            ),

            avg_spend=(
                "bid_amount",
                "mean"
            ),

            avg_bid=(
                "bid_amount",
                "mean"
            ),

            avg_max_bid=(
                "bid_amount",
                "max"
            ),

            avg_early_spending=(
                "draft_phase",
                lambda x:
                (x == "early").mean() * 100
            ),

            avg_aggression=(
                "league_price_percentile",
                "mean"
            ),

            avg_patience=(
                "remaining_budget",
                "mean"
            ),

            avg_stars_scrubs=(
                "is_elite_purchase",
                "mean"
            )
        )
        .reset_index()
    )


    manager["avg_early_spending"] = (
        manager["avg_early_spending"]
        .round(1)
    )


    manager["avg_aggression"] = (
        manager["avg_aggression"]
        .mul(100)
        .round(1)
    )


    manager["avg_patience"] = (
        manager["avg_patience"]
        .rank(pct=True)
        .mul(100)
        .round(1)
    )


    manager["avg_stars_scrubs"] = (
        manager["avg_stars_scrubs"]
        .mul(100)
        .round(1)
    )


    manager["archetype"] = (
        manager.apply(
            classify_archetype,
            axis=1
        )
    )


    manager["draft_strategy"] = (
        manager["archetype"]
        .apply(
            strategy_description
        )
    )


    return manager



def main():

    auction = load_table(
        "auction_features"
    )

    report = build_personality_features(
        auction
    )

    save_report(
        report,
        "manager_personality_career.csv"
    )

    print(report)



if __name__ == "__main__":
    main()