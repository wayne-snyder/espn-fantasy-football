"""
Core feature engineering functions.

This module contains reusable calculations used by all analytics.
No reports should calculate these directly.
"""

import pandas as pd


def add_running_spend(df):
    """
    Adds cumulative auction spending by manager and season.
    """

    df = df.sort_values(
        [
            "season",
            "fantasy_team_id",
            "pick_number"
        ]
    )

    df["running_spend"] = (
        df.groupby(
            [
                "season",
                "fantasy_team_id"
            ]
        )["bid_amount"]
        .cumsum()
    )

    return df



def add_remaining_budget(
    df,
    budget=200
):
    """
    Calculates remaining auction money.
    """

    df["remaining_budget"] = (
        budget - df["running_spend"]
    )

    return df



def add_roster_slots(
    df,
    roster_size=16
):
    """
    Calculates roster availability.
    """

    df["players_bought"] = (
        df.groupby(
            [
                "season",
                "fantasy_team_id"
            ]
        )
        .cumcount()
        + 1
    )

    df["remaining_roster_spots"] = (
        roster_size -
        df["players_bought"]
    )

    return df



def add_budget_pressure(df):
    """
    Determines how desperate a manager is
    based on remaining money and roster slots.
    """

    df["avg_dollars_per_open_slot"] = (
        df["remaining_budget"]
        /
        df["remaining_roster_spots"]
        .clip(lower=1)
    )

    return df



def add_position_purchase_number(df):
    """
    Tracks order of purchases within position.
    """

    df["position_purchase_number"] = (
        df.groupby(
            [
                "season",
                "fantasy_team_id",
                "position"
            ]
        )
        .cumcount()
        + 1
    )

    return df



def build_auction_features(
    df
):
    """
    Master auction feature pipeline.
    """

    df = df.copy()

    df = add_running_spend(df)

    df = add_remaining_budget(df)

    df = add_roster_slots(df)

    df = add_budget_pressure(df)

    df = add_position_purchase_number(df)

    return df