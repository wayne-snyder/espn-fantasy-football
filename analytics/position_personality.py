"""
Analyzes auction position spending behavior.

Answers:
- Who spends heavily on RB?
- Who prioritizes WR?
- Who ignores QB?
- Who chases TE?
"""

from db_utils import load_table, save_report


def main():

    picks = load_table(
        "auction_picks"
    )


    position_spending = (
        picks.groupby(
            [
                "season",
                "fantasy_team",
                "position"
            ]
        )
        .agg(
            dollars_spent=(
                "bid_amount",
                "sum"
            ),
            players_bought=(
                "player_id",
                "count"
            ),
            avg_bid=(
                "bid_amount",
                "mean"
            )
        )
        .reset_index()
    )


    total = (
        position_spending
        .groupby(
            [
                "season",
                "fantasy_team"
            ]
        )["dollars_spent"]
        .transform("sum")
    )


    position_spending[
        "pct_of_budget"
    ] = (
        position_spending[
            "dollars_spent"
        ]
        /
        total
        *
        100
    ).round(1)


    position_spending[
        "avg_bid"
    ] = (
        position_spending[
            "avg_bid"
        ]
        .round(2)
    )


    position_spending = position_spending.sort_values(
        [
            "season",
            "fantasy_team",
            "pct_of_budget"
        ],
        ascending=[
            True,
            True,
            False
        ]
    )


    print(position_spending)

    save_report(
        position_spending,
        "position_personality.csv"
    )


if __name__ == "__main__":
    main()