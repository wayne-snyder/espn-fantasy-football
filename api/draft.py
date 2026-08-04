def get_draft_history(client, season, league_id):
    return client.get_draft(season, league_id)


def extract_auction_picks(season, draft_data):

    picks = []

    draft = draft_data["draftDetail"]["picks"]

    for pick in draft:
        picks.append(
            {
                "season": season,
                "pick_id": pick.get("id"),
                "player_id": pick.get("playerId"),
                "team_id": pick.get("teamId"),
                "bid_amount": pick.get("bidAmount"),
                "keeper": pick.get("keeper"),
                "round": pick.get("round"),
            }
        )

    return picks
