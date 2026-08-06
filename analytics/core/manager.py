import pandas as pd


def add_manager_scores(df):

    df = df.copy()

    # Normalize league behavior
    df["aggression_z"] = (
        df["avg_aggression"]
        - df["avg_aggression"].mean()
    ) / df["avg_aggression"].std()


    df["patience_z"] = (
        df["avg_patience"]
        - df["avg_patience"].mean()
    ) / df["avg_patience"].std()


    df["stars_z"] = (
        df["avg_stars_scrubs"]
        - df["avg_stars_scrubs"].mean()
    ) / df["avg_stars_scrubs"].std()


    df["max_bid_z"] = (
        df["avg_max_bid"]
        - df["avg_max_bid"].mean()
    ) / df["avg_max_bid"].std()


    # Weighted auction personalities

    df["aggression_score"] = (
        df["aggression_z"] * .50
        +
        df["max_bid_z"] * .30
        -
        df["patience_z"] * .20
    )


    df["patience_score"] = (
        df["patience_z"] * .70
        -
        df["aggression_z"] * .30
    )


    df["stars_scrubs_score"] = (
        df["stars_z"]
    )


    return df



def add_manager_percentiles(df):

    df = df.copy()

    for col in [
        "aggression_score",
        "patience_score",
        "stars_scrubs_score"
    ]:

        df[f"{col}_percentile"] = (
            df[col]
            .rank(pct=True)
        )


    return df



def classify_manager(row):

    aggression = row["aggression_score_percentile"]

    patience = row["patience_score_percentile"]

    stars = row["stars_scrubs_score_percentile"]


    # Highest concentration on stars
    if stars >= .75:
        return "The Whale"


    # Most aggressive spenders
    if aggression >= .75:
        return "The Shark"


    # Patient value seekers
    if patience >= .75:
        return "The Sniper"


    # Conservative managers
    if aggression <= .25 and stars < .60:
        return "The Value Hunter"


    return "Balanced"



def assign_secondary_trait(row):

    traits=[]


    if row["stars_scrubs_score_percentile"] >= .75:
        traits.append(
            "Stars & Scrubs"
        )


    if row["aggression_score_percentile"] >= .75:
        traits.append(
            "Aggressive Spending"
        )


    if row["patience_score_percentile"] >= .75:
        traits.append(
            "Late Value"
        )


    if row["favorite_positions"]:
        traits.append(
            row["favorite_positions"]
            .split(",")[0]
            .strip()
            +
            " Preference"
        )


    return ", ".join(traits)



def calculate_confidence(row):

    seasons=row["seasons_active"]

    if seasons >=4:
        return "High"

    if seasons >=2:
        return "Medium"

    return "Low"



def generate_strategy(row):

    strategies={

        "The Shark":
        "Attack their preferred players early. Let them spend aggressively and preserve budget.",

        "The Whale":
        "Avoid competing for elite players. Target depth after they exhaust premium capital.",

        "The Sniper":
        "Expect late value hunting. Secure targets before the endgame discount window.",

        "The Value Hunter":
        "Pressure them with nominations outside their comfort zone.",

        "Balanced":
        "No dominant behavioral pattern. Adjust based on roster construction."

    }

    return strategies[row["primary_archetype"]]



def build_manager_profiles(df):

    df=add_manager_scores(df)

    df=add_manager_percentiles(df)


    df["primary_archetype"]=df.apply(
        classify_manager,
        axis=1
    )


    df["secondary_trait"]=df.apply(
        assign_secondary_trait,
        axis=1
    )


    df["confidence"]=df.apply(
        calculate_confidence,
        axis=1
    )


    df["draft_strategy"]=df.apply(
        generate_strategy,
        axis=1
    )


    return df