"""
Build manager history dimension.

Creates a persistent manager identity table from ESPN team history.

Input:
    teams

Output:
    manager_history
"""

from db_utils import load_table, get_connection

import pandas as pd


def build_manager_history(teams):

    teams = teams.copy()

    teams["manager_id"] = teams["owner"]

    manager_history = (
        teams.groupby("manager_id")
        .agg(
            seasons_active=("season", "nunique"),
            first_season=("season", "min"),
            last_season=("season", "max"),
            team_names=("team_name", lambda x: ", ".join(sorted(set(x)))),
            seasons=("season", lambda x: ", ".join(
                map(str, sorted(set(x)))
            )),
        )
        .reset_index()
    )

    return manager_history


def save_table(df, table_name):

    conn = get_connection()

    df.to_sql(
        table_name,
        conn,
        if_exists="replace",
        index=False
    )

    conn.close()


def main():

    teams = load_table("teams")

    manager_history = build_manager_history(
        teams
    )

    save_table(
        manager_history,
        "manager_history"
    )

    print(
        f"Created manager_history ({len(manager_history)} rows)"
    )

    print(manager_history)


if __name__ == "__main__":
    main()