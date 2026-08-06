"""
Auction analytics helpers.
"""

import pandas as pd



def calculate_spend_share(df):

    totals = (
        df.groupby(
            [
                "season",
                "fantasy_team_id"
            ]
        )["bid_amount"]
        .transform("sum")
    )

    df["spend_share"] = (
        df["bid_amount"]
        /
        totals
    )

    return df



def calculate_price_percentile(df):

    df["league_price_percentile"] = (
        df.groupby("season")
        ["bid_amount"]
        .rank(
            pct=True
        )
    )

    return df



def calculate_position_percentile(df):

    df["position_price_percentile"] = (
        df.groupby(
            [
                "season",
                "position"
            ]
        )
        ["bid_amount"]
        .rank(
            pct=True
        )
    )

    return df



def build_auction_dataset(df):

    df = calculate_spend_share(df)

    df = calculate_price_percentile(df)

    df = calculate_position_percentile(df)

    return df