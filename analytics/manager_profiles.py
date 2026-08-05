"""
Creates human-readable manager scouting profiles.
"""

from db_utils import load_table, save_report


def classify_manager(row):

    aggression = row["avg_aggression"]
    patience = row["avg_patience"]
    stars = row["avg_stars_scrubs"]


    if aggression >= 70 and patience < 40:
        return "The Shark"

    if stars >= 80:
        return "The Whale"

    if patience >= 75:
        return "The Sniper"

    if aggression < 35:
        return "The Value Hunter"

    return "Balanced"


def recommendation(row):

    archetype = row["archetype"]


    advice = {

        "The Shark":
            "Avoid bidding wars. Let them overpay early.",

        "The Whale":
            "Allow premium purchases. Attack value after budget is committed.",

        "The Sniper":
            "Do not leave bargains uncontested late.",

        "The Value Hunter":
            "Increase nomination pressure and force spending.",

        "Balanced":
            "Use normal auction strategy."
    }


    return advice.get(
        archetype,
        ""
    )


def main():

    personality = load_table(
        "auction_personality_career"
    )


    personality[
        "archetype"
    ] = personality.apply(
        classify_manager,
        axis=1
    )


    personality[
        "draft_strategy"
    ] = personality.apply(
        recommendation,
        axis=1
    )


    personality = personality.sort_values(
        "avg_aggression",
        ascending=False
    )


    print(personality)

    save_report(
        personality,
        "manager_profiles.csv"
    )


if __name__ == "__main__":
    main()