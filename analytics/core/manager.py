"""
Manager personality engine.

Creates fantasy auction manager profiles from manager_features.

Responsible for:
- behavioral scoring
- archetype classification
- secondary traits
- confidence scoring
- draft strategy recommendations
"""

import pandas as pd



def add_manager_scores(df):
    """
    Creates normalized behavior scores.
    """

    df = df.copy()


    max_bid = df["avg_max_bid"].max()

    if max_bid <= 0:
        max_bid = 1


    # Aggression:
    # Heavy bids + aggressive purchases + early spending behavior

    df["aggression_score"] = (
        df["avg_aggression"] * 0.50
        +
        (100 - df["avg_patience"]) * 0.30
        +
        (
            df["avg_max_bid"]
            /
            max_bid
            *
            100
        ) * 0.20
    )


    # Patience:
    # Waiting for value and avoiding early spending

    df["patience_score"] = (
        df["avg_patience"] * 0.70
        +
        (100 - df["avg_aggression"]) * 0.30
    )


    # Stars and scrubs tendency

    df["stars_scrubs_score"] = (
        df["avg_stars_scrubs"]
    )


    return df



def classify_manager(row):
    """
    Determines primary manager archetype.
    """

    aggression = row["avg_aggression"]

    patience = row["avg_patience"]

    stars = row["avg_stars_scrubs"]


    # Aggressive bidders
    if aggression >= 33:
        return "The Shark"


    # Concentrates budget into elite players
    if stars >= 60:
        return "The Whale"


    # Patient bargain hunter
    if patience >= 20:
        return "The Sniper"


    # Avoids spending
    if aggression <= 22:
        return "The Value Hunter"


    return "Balanced"



def assign_secondary_trait(row):
    """
    Adds additional tendencies.
    """

    traits = []


    if row["avg_stars_scrubs"] >= 55:
        traits.append(
            "Stars & Scrubs"
        )


    favorite = row.get(
        "favorite_positions",
        ""
    )

    if isinstance(favorite, str) and favorite:

        traits.append(
            favorite.split(",")[0].strip()
            +
            " Heavy"
        )


    if row["avg_patience"] <= 10:

        traits.append(
            "Fast Starter"
        )


    elif row["avg_patience"] >= 20:

        traits.append(
            "Late Value"
        )


    if not traits:

        return "No strong secondary tendency"


    return ", ".join(traits)



def calculate_confidence(row):
    """
    Confidence based on available seasons.
    """

    seasons = row["seasons_active"]


    if seasons >= 4:
        return "High"


    if seasons >= 2:
        return "Medium"


    return "Low"



def generate_strategy(row):
    """
    Generates auction advice.
    """

    strategies = {

        "The Shark":
            (
                "Expect aggressive bidding. "
                "Avoid unnecessary wars and let them drain budget."
            ),


        "The Whale":
            (
                "Expect premium player attacks. "
                "Target depth and value after elite purchases."
            ),


        "The Sniper":
            (
                "Watch late auction opportunities. "
                "Protect discounted players from slipping away."
            ),


        "The Value Hunter":
            (
                "Increase nomination pressure. "
                "Force uncomfortable spending decisions."
            ),


        "Balanced":
            (
                "No extreme tendency identified. "
                "Use standard auction tactics."
            )
    }


    return strategies.get(
        row["primary_archetype"],
        ""
    )



def build_manager_profiles(df):
    """
    Complete manager personality pipeline.
    """

    df = df.copy()


    df = add_manager_scores(
        df
    )


    df["primary_archetype"] = (
        df.apply(
            classify_manager,
            axis=1
        )
    )


    df["secondary_trait"] = (
        df.apply(
            assign_secondary_trait,
            axis=1
        )
    )


    df["confidence"] = (
        df.apply(
            calculate_confidence,
            axis=1
        )
    )


    df["draft_strategy"] = (
        df.apply(
            generate_strategy,
            axis=1
        )
    )


    return df