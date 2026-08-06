"""
Creates manager personality profiles.

This report consumes the manager personality engine
from analytics.core.manager.
"""

from db_utils import load_table, save_report, save_table
from core.manager import build_manager_profiles


def main():

    features = load_table(
        "manager_features"
    )

    try:
        manager_history = load_table("manager_history")
        features = features.merge(
            manager_history[["manager_id", "manager_name"]],
            on="manager_id",
            how="left",
        )
    except Exception:
        features["manager_name"] = None

    profiles = build_manager_profiles(
        features
    )


    # Sort strongest personalities first
    profiles = profiles.sort_values(
        [
            "primary_archetype",
            "aggression_score"
        ],
        ascending=[
            True,
            False
        ]
    )


    columns = [
        "manager_id",

        "manager_name",

        "seasons_active",

        "avg_spend",

        "avg_bid",

        "avg_max_bid",

        "avg_aggression",

        "avg_patience",

        "avg_stars_scrubs",

        "aggression_score",

        "patience_score",

        "stars_scrubs_score",

        "primary_archetype",

        "secondary_trait",

        "confidence",

        "favorite_positions",

        "draft_strategy"
    ]


    # Only select columns that exist
    columns = [
        col for col in columns
        if col in profiles.columns
    ]


    profiles = profiles[
        columns
    ]


    print(
        profiles.to_string()
    )


    save_report(
        profiles,
        "manager_profiles.csv"
    )

    save_table(
        profiles,
        "manager_profiles"
    ) 


if __name__ == "__main__":
    main()