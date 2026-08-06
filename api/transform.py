from api.constants import PLAYER_POSITION_MAP


def build_player_lookup(players):

    lookup = {}

    for player in players:

        position_id = player.get("defaultPositionId")

        lookup[player["id"]] = {
            "player_name": player.get("fullName"),
            "position": PLAYER_POSITION_MAP.get(position_id, position_id),
            "nfl_team": player.get("proTeamId"),
        }

    return lookup


def flatten_players_from_rosters(teams):
    """
    mTeam/mRoster views don't return a top-level "players" list —
    each team's roster nests player info under
    team["roster"]["entries"][i]["playerPoolEntry"]["player"].
    This walks every team's roster and returns a flat list of player
    dicts in the same shape build_player_lookup() expects.
    """

    players = []
    seen_ids = set()

    for team in teams:

        entries = team.get("roster", {}).get("entries", [])

        for entry in entries:

            player = entry.get("playerPoolEntry", {}).get("player", {})

            player_id = player.get("id")

            if player_id is None or player_id in seen_ids:
                continue

            seen_ids.add(player_id)
            players.append(player)

    return players


def build_team_lookup(teams):

    lookup = {}

    for team in teams:

        owners = team.get("owners", [])

        lookup[team["id"]] = {
            "team_name": team.get("name"),
            "abbrev": team.get("abbrev"),
            "owners": owners,
            "owner": owners[0] if owners else None,
        }

    return lookup


def build_manager_lookup(users):
    """
    users: league["members"] — already included in the same league
    response you fetch with mTeam/mRoster/mSettings. No separate API
    call needed.
    """

    lookup = {}

    for user in users:

        user_id = user.get("id")

        if not user_id:
            continue

        lookup[user_id] = {
            "manager_id": user_id,
            "manager_name": (
                user.get("displayName")
                or user.get("firstName")
                or user_id
            ),
        }

    return lookup


def transform_draft(
    draft_data,
    player_lookup,
    team_lookup,
    season
):

    results = []

    picks = draft_data["draftDetail"]["picks"]

    for pick in picks:

        player = player_lookup.get(
            pick["playerId"],
            {}
        )

        team = team_lookup.get(
            pick["teamId"],
            {}
        )

        results.append(
            {
                "season": season,

                "pick_number": pick.get(
                    "overallPickNumber"
                ),

                "player_id": pick.get(
                    "playerId"
                ),

                "player_name": player.get(
                    "player_name"
                ),

                "position": player.get(
                    "position"
                ),

                "nfl_team": player.get(
                    "nfl_team"
                ),

                "fantasy_team_id": pick.get(
                    "teamId"
                ),

                "fantasy_team": team.get(
                    "team_name"
                ),

                "bid_amount": pick.get(
                    "bidAmount"
                ),

                "keeper": pick.get(
                    "keeper"
                ),

                "round": pick.get(
                    "round"
                ),
            }
        )

    return results


def transform_settings(league_data, season):
    """
    Flattens the mSettings portion of a league response into one row
    per season: league name, team count, auction budget, roster size,
    and playoff format. Field names come from ESPN's documented
    mSettings schema — worth spot-checking against your actual league's
    JSON dump in output/ the first time you run this, since ESPN's
    private API isn't officially documented and has been known to shift.
    """

    settings = league_data.get("settings", {})

    draft_settings = settings.get("draftSettings", {})
    roster_settings = settings.get("rosterSettings", {})
    schedule_settings = settings.get("scheduleSettings", {})

    lineup_slot_counts = roster_settings.get("lineupSlotCounts", {})

    return {
        "season": season,
        "league_name": settings.get("name"),
        "team_count": settings.get("size"),
        "is_auction": draft_settings.get("type") == "OFFLINE_AUCTION"
        or draft_settings.get("type") == "AUCTION",
        "auction_budget": draft_settings.get("budget"),
        "roster_size": sum(lineup_slot_counts.values())
        if lineup_slot_counts
        else None,
        "playoff_team_count": schedule_settings.get("playoffTeamCount"),
    }
