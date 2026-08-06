"""
Lineup analytics core functions.

This module contains reusable lineup calculations.
Analytics reports should consume these functions rather than
rebuilding lineup logic independently.
"""

import pandas as pd



def calculate_optimal_points(lineups):
    """
    Calculates theoretical maximum points for each team/week.

    Uses all players on the roster and selects the highest scoring
    legal lineup based on the available starters.

    Current implementation calculates the maximum available points
    without enforcing roster slot restrictions.
    """

    optimal = (
        lineups
        .groupby(
            [
                "season",
                "week",
                "team_id"
            ]
        )
        ["points"]
        .sum()
        .reset_index()
        .rename(
            columns={
                "points": "optimal_points"
            }
        )
    )

    return optimal



def calculate_actual_points(lineups):
    """
    Calculates actual starting lineup points.
    """

    starters = lineups[
        lineups["is_starter"] == True
    ]

    actual = (
        starters
        .groupby(
            [
                "season",
                "week",
                "team_id"
            ]
        )
        ["points"]
        .sum()
        .reset_index()
        .rename(
            columns={
                "points": "actual_points"
            }
        )
    )

    return actual



def calculate_bench_points(lineups):
    """
    Calculates points left on bench.
    """

    bench = lineups[
        lineups["is_starter"] == False
    ]

    result = (
        bench
        .groupby(
            [
                "season",
                "week",
                "team_id"
            ]
        )
        ["points"]
        .sum()
        .reset_index()
        .rename(
            columns={
                "points": "bench_points"
            }
        )
    )

    return result



def calculate_lineup_efficiency(lineups):
    """
    Measures percentage of available points captured.

    Formula:

        actual starter points
        --------------------
        optimal roster points
    """

    actual = calculate_actual_points(
        lineups
    )

    optimal = calculate_optimal_points(
        lineups
    )

    result = actual.merge(
        optimal,
        on=[
            "season",
            "week",
            "team_id"
        ],
        how="left"
    )


    result["lineup_efficiency"] = (
        result["actual_points"]
        /
        result["optimal_points"]
        .replace(0, pd.NA)
    )


    result["points_left_on_bench"] = (
        result["optimal_points"]
        -
        result["actual_points"]
    )


    return result



def calculate_manager_lineup_skill(lineup_results):
    """
    Aggregates lineup decisions by manager/team.

    Produces long-term lineup management score.
    """

    skill = (
        lineup_results
        .groupby(
            "team_id"
        )
        .agg(
            avg_efficiency=(
                "lineup_efficiency",
                "mean"
            ),

            avg_points_left=(
                "points_left_on_bench",
                "mean"
            ),

            weeks_evaluated=(
                "week",
                "count"
            )
        )
        .reset_index()
    )

    return skill