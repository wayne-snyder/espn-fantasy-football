"""
Creates manager identity profiles across seasons.

Uses ESPN owner ID as the permanent manager identifier
and tracks team names across seasons.
"""

from db_utils import load_table, save_report


def main():

    teams = load_table("teams")


    identity = (
        teams.groupby("owner")
        .agg(
            seasons=(
                "season",
                "nunique"
            ),

            team_names=(
                "team_name",
                lambda x:
                    ", ".join(
                        sorted(set(x))
                    )
            ),

            fantasy_team_ids=(
                "team_id",
                lambda x:
                    ", ".join(
                        map(
                            str,
                            sorted(set(x))
                        )
                    )
            )
        )
        .reset_index()
    )


    identity = identity.sort_values(
        "seasons",
        ascending=False
    )


    print(identity)

    save_report(
        identity,
        "manager_identity.csv"
    )


if __name__ == "__main__":
    main()