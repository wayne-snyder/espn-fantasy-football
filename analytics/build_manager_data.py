"""
Creates analytics-ready auction data with stable manager IDs.
"""

import sqlite3
import pandas as pd

from db_utils import get_connection


def main():

    conn = get_connection()

    auction = pd.read_sql(
        "SELECT * FROM auction_picks",
        conn
    )

    teams = pd.read_sql(
        "SELECT * FROM teams",
        conn
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


    enriched.to_sql(
        "auction_picks_enriched",
        conn,
        if_exists="replace",
        index=False
    )


    conn.close()


    print(
        f"Created auction_picks_enriched ({len(enriched)} rows)"
    )


if __name__ == "__main__":
    main()