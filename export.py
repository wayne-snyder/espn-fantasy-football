import pandas as pd
from tqdm import tqdm

from api.client import ESPNClient
from api.draft import get_draft_history, extract_auction_picks
from api.matchups import (
    extract_matchup_results,
    extract_weekly_lineups,
    get_boxscore,
    get_final_week,
)
from api.transform import (
    build_player_lookup,
    build_team_lookup,
    flatten_players_from_rosters,
    transform_draft,
    transform_settings,
)
from config import LEAGUE_ID, START_YEAR, END_YEAR
from storage import dump_json, get_db_connection, write_csv, write_excel, write_to_db


def main():

    client = ESPNClient()

    all_picks = []
    all_settings = []
    all_lineups = []
    all_matchups = []
    all_teams = []

    for season in tqdm(range(START_YEAR, END_YEAR + 1), desc="Seasons"):

        league = client.get(season, LEAGUE_ID, ["mTeam", "mRoster", "mSettings"])
        dump_json(league, season, "league")

        draft_data = get_draft_history(client, season, LEAGUE_ID)
        dump_json(draft_data, season, "draft")

        players = flatten_players_from_rosters(league.get("teams", []))
        player_lookup = build_player_lookup(players)
        team_lookup = build_team_lookup(league.get("teams", []))

        picks = transform_draft(draft_data, player_lookup, team_lookup, season)
        all_picks.extend(picks)

        settings_row = transform_settings(league, season)
        all_settings.append(settings_row)

        for team_id, team_info in team_lookup.items():
            all_teams.append(
                {
                    "season": season,
                    "team_id": team_id,
                    "team_name": team_info.get("team_name"),
                    "abbrev": team_info.get("abbrev"),
                    "owner": ", ".join(team_info.get("owner") or []),
                }
            )

        # Weekly box scores: needed for value-vs-cost, lineup efficiency,
        # power rankings, and luck index. Looped week by week since ESPN's
        # boxscore view only returns the data for the scoringPeriodId
        # you pass in.
        final_week = get_final_week(league)

        for week in tqdm(
            range(1, final_week + 1), desc=f"  {season} weeks", leave=False
        ):

            boxscore_data = get_boxscore(client, season, LEAGUE_ID, week)
            dump_json(boxscore_data, season, f"week{week}_boxscore")

            all_lineups.extend(
                extract_weekly_lineups(boxscore_data, season, week)
            )
            all_matchups.extend(
                extract_matchup_results(boxscore_data, season, week)
            )

    picks_df = pd.DataFrame(all_picks)
    settings_df = pd.DataFrame(all_settings)
    lineups_df = pd.DataFrame(all_lineups)
    matchups_df = pd.DataFrame(all_matchups)
    teams_df = pd.DataFrame(all_teams).drop_duplicates()

    # Polished exports
    write_csv(picks_df, "auction_history.csv")
    write_csv(settings_df, "league_settings.csv")
    write_csv(lineups_df, "weekly_lineups.csv")
    write_csv(matchups_df, "weekly_matchups.csv")
    write_csv(teams_df, "teams.csv")

    write_excel(
        {
            "Auction History": picks_df,
            "League Settings": settings_df,
            "Weekly Lineups": lineups_df,
            "Weekly Matchups": matchups_df,
            "Teams": teams_df,
        },
        "espn_fantasy_export.xlsx",
    )

    # Persist to SQLite for the analytics/ reports and future querying
    conn = get_db_connection()
    write_to_db(conn, picks_df, "auction_picks")
    write_to_db(conn, settings_df, "league_settings")
    write_to_db(conn, lineups_df, "weekly_lineups")
    write_to_db(conn, matchups_df, "weekly_matchups")
    write_to_db(conn, teams_df, "teams")
    conn.close()

    print(
        f"Exported {len(picks_df)} auction picks, "
        f"{len(lineups_df)} weekly lineup rows, "
        f"and {len(matchups_df)} weekly matchup rows "
        f"across {len(settings_df)} season(s)."
    )
    print("Raw JSON dumps      -> output/")
    print("Polished CSV/Excel  -> exports/")
    print("SQLite database     -> database/")


if __name__ == "__main__":
    main()
