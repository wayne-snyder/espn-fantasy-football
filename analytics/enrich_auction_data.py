"""
Adds stable manager IDs to auction history.
"""

from db_utils import load_table, save_report


def main():

    auction = load_table(
        "auction_picks"
    )

    teams = load_table(
        "teams"
    )


    enriched = auction.merge(
        teams[
            [
                "season",
                "team_id",
                "owner",
                "team_name"
            ]
        ],
        left_on=[
            "season",
            "fantasy_team_id"
        ],
        right_on=[
            "season",
            "team_id"
        ],
        how="left"
    )


    enriched = enriched.rename(
        columns={
            "owner": "manager_id"
        }
    )


    save_report(
        enriched,
        "auction_history_enriched.csv"
    )


    print(
        enriched[
            [
                "season",
                "manager_id",
                "team_name",
                "player_name",
                "bid_amount"
            ]
        ].head()
    )


if __name__ == "__main__":
    main()