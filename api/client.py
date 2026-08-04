import requests

from config import ESPN_S2
from config import SWID
from config import REQUEST_TIMEOUT


class ESPNClient:

    BASE_URL = (
        "https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl"
    )

    def __init__(self):

        self.session = requests.Session()

        self.session.cookies.set("SWID", SWID)
        self.session.cookies.set("espn_s2", ESPN_S2)

    def get_draft(self, season: int, league_id: int):
        return self.get(
            season,
            league_id,
            ["mDraftDetail"]
        )

    def get_boxscore(self, season: int, league_id: int, scoring_period_id: int):
        """
        Weekly box score: each team's roster for that week with each
        player's lineup slot (starter/bench/IR) and points scored.
        scoring_period_id is the fantasy week number (1, 2, 3, ...).
        """
        return self.get(
            season,
            league_id,
            ["mBoxscore", "mMatchupScore"],
            extra_params=[("scoringPeriodId", scoring_period_id)],
        )

    def get(self, season: int, league_id: int, views, extra_params=None):

        params = []

        for view in views:
            params.append(("view", view))

        if extra_params:
            params.extend(extra_params)

        url = (
            f"{self.BASE_URL}/seasons/"
            f"{season}/segments/0/leagues/{league_id}"
        )

        response = self.session.get(
            url,
            params=params,
            timeout=REQUEST_TIMEOUT,
        )

        response.raise_for_status()

        return response.json()