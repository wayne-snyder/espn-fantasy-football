"""
Build manager history dimension.

Creates a persistent manager identity table from ESPN team history.

Input:
    teams

Output:
    manager_history
"""

from db_utils import load_table, save_table

import pandas as pd


def build_manager_history(teams, managers):

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

    if not managers.empty:
        # managers has one row per (manager_id, season) since ESPN
        # sends the member list per-season fetch; take the most recent
        # display name on record for each manager_id
        latest_names = (
            managers.sort_values("season")
            .drop_duplicates("manager_id", keep="last")[
                ["manager_id", "manager_name"]
            ]
        )
        manager_history = manager_history.merge(
            latest_names, on="manager_id", how="left"
        )
    else:
        manager_history["manager_name"] = None

    return manager_history


def main():

    teams = load_table("teams")

    try:
        managers = load_table("managers")
    except Exception:
        managers = pd.DataFrame(columns=["manager_id", "manager_name", "season"])

    manager_history = build_manager_history(
        teams,
        managers
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