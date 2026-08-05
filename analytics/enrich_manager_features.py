"""
Builds the master auction analytics table.

Input:
    auction_picks_enriched

Output:
    auction_features

Every future analytics module should read from auction_features.
"""

import numpy as np
import pandas as pd

from db_utils import get_connection


BUDGET = 200


def draft_phase(pick):
    if pick <= 64:
        return "Early"
    elif pick <= 128:
        return "Middle"
    return "Late"


def price_tier(bid):

    if bid >= 50:
        return "Elite"

    if bid >= 30:
        return "Premium"

    if bid >= 15:
        return "Starter"

    if bid >= 5:
        return "Depth"

    if bid >= 2:
        return "Bargain"

    return "$1"


def main():

    conn = get_connection()

    df = pd.read_sql(
        "SELECT * FROM auction_picks_enriched",
        conn
    )

    # ----------------------------
    # Basic engineered features
    # ----------------------------

    df["bid_pct_budget"] = (
        df["bid_amount"] / BUDGET * 100
    ).round(2)

    df["draft_phase"] = df["pick_number"].apply(
        draft_phase
    )

    df["price_tier"] = df["bid_amount"].apply(
        price_tier
    )

    df["is_elite_purchase"] = (
        df["bid_amount"] >= 50
    )

    df["is_value_purchase"] = (
        df["bid_amount"] <= 5
    )

    # ----------------------------
    # Purchase order
    # ----------------------------

    df = df.sort_values(
        [
            "season",
            "manager_id",
            "pick_number"
        ]
    )

    df["purchase_number"] = (
        df.groupby(
            [
                "season",
                "manager_id"
            ]
        )
        .cumcount()
        + 1
    )

    # ----------------------------
    # Remaining budget
    # ----------------------------

    df["running_spend"] = (
        df.groupby(
            [
                "season",
                "manager_id"
            ]
        )["bid_amount"]
        .cumsum()
    )

    df["remaining_budget"] = (
        BUDGET - df["running_spend"]
    )

    # ----------------------------
    # Remaining roster spots
    # ----------------------------

    roster_size = (
        df.groupby(
            [
                "season",
                "manager_id"
            ]
        )["purchase_number"]
        .transform("max")
    )

    df["remaining_roster_spots"] = (
        roster_size - df["purchase_number"]
    )

    # ----------------------------
    # Average dollars remaining
    # ----------------------------

    df["avg_dollars_per_open_slot"] = np.where(
        df["remaining_roster_spots"] > 0,
        (
            df["remaining_budget"]
            /
            df["remaining_roster_spots"]
        ).round(2),
        0
    )

    # ----------------------------
    # Positional purchase order
    # ----------------------------

    df["position_purchase_number"] = (
        df.groupby(
            [
                "season",
                "manager_id",
                "position"
            ]
        )
        .cumcount()
        + 1
    )

    # ----------------------------
    # Price percentile
    # ----------------------------

    df["league_price_percentile"] = (
        df.groupby("season")["bid_amount"]
        .rank(pct=True)
        .round(3)
    )

    # ----------------------------
    # Positional percentile
    # ----------------------------

    df["position_price_percentile"] = (
        df.groupby(
            [
                "season",
                "position"
            ]
        )["bid_amount"]
        .rank(pct=True)
        .round(3)
    )

    # ----------------------------
    # Save
    # ----------------------------

    df.to_sql(
        "auction_features",
        conn,
        if_exists="replace",
        index=False
    )

    conn.close()

    print(f"Created auction_features ({len(df)} rows)")
    print()
    print(df.head(15))


if __name__ == "__main__":
    main()