"""
Generates auction strategies from manager personality profiles.

Consumes:
    manager_profiles

Produces:
    auction_strategy.csv
"""

from db_utils import load_table, save_report


def generate_strategy(row):
    """
    Creates actionable auction recommendations.
    """

    archetype = row["primary_archetype"]

    strategies = {

        "The Whale": {
            "strength":
                "Aggressively acquires premium talent.",

            "weakness":
                "Can leave roster depth vulnerable.",

            "exploit_strategy":
                "Avoid premium bidding wars. Let them spend budget, then attack value.",

            "avoid_strategy":
                "Do not chase elite players against this manager.",

            "target_strategy":
                "Prioritize mid-tier starters after their major purchases."
        },


        "The Shark": {
            "strength":
                "Willing to spend aggressively and influence prices.",

            "weakness":
                "May overpay early.",

            "exploit_strategy":
                "Force expensive decisions early. Do not compete emotionally.",

            "avoid_strategy":
                "Avoid unnecessary bidding battles.",

            "target_strategy":
                "Save budget and attack discounted late players."
        },


        "The Sniper": {
            "strength":
                "Patient and disciplined with spending.",

            "weakness":
                "May wait too long on targets.",

            "exploit_strategy":
                "Increase nomination pressure on players they likely value.",

            "avoid_strategy":
                "Do not assume late value will always be available.",

            "target_strategy":
                "Secure players before endgame discounts disappear."
        },


        "The Value Hunter": {
            "strength":
                "Finds discounts and avoids overpaying.",

            "weakness":
                "Can hesitate on premium talent.",

            "exploit_strategy":
                "Push prices slightly above their comfort zone.",

            "avoid_strategy":
                "Do not expect them to chase expensive players.",

            "target_strategy":
                "Use aggressive nominations to drain their budget."
        },


        "Balanced": {
            "strength":
                "No major behavioral weakness detected.",

            "weakness":
                "Less predictable.",

            "exploit_strategy":
                "Use standard auction principles.",

            "avoid_strategy":
                "Avoid assuming predictable tendencies.",

            "target_strategy":
                "Prioritize roster construction over matchup tactics."
        }
    }


    result = strategies.get(
        archetype,
        strategies["Balanced"]
    )


    return result



def build_auction_strategy(profiles):

    rows = []

    for _, row in profiles.iterrows():

        strategy = generate_strategy(row)

        rows.append(
            {
                "manager_id":
                    row["manager_id"],

                "primary_archetype":
                    row["primary_archetype"],

                "confidence":
                    row["confidence"],

                "favorite_positions":
                    row["favorite_positions"],

                "strength":
                    strategy["strength"],

                "weakness":
                    strategy["weakness"],

                "exploit_strategy":
                    strategy["exploit_strategy"],

                "avoid_strategy":
                    strategy["avoid_strategy"],

                "target_strategy":
                    strategy["target_strategy"],
            }
        )


    return __import__("pandas").DataFrame(rows)



def main():

    profiles = load_table(
        "manager_profiles"
    )


    strategy = build_auction_strategy(
        profiles
    )


    print(strategy)


    save_report(
        strategy,
        "auction_strategy.csv"
    )



if __name__ == "__main__":
    main()