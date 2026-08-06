"""
Configuration for ESPN Fantasy Exporter

SWID and ESPN_S2 are your ESPN session cookies — treat them like a
password. They're loaded from .env (gitignored, never committed)
rather than hardcoded here. See .env.example for the expected format.
"""

import os

from dotenv import load_dotenv

load_dotenv()

LEAGUE_ID = 119210          # Replace with your league id

START_YEAR = 2022
END_YEAR = 2025

SWID = os.environ.get("SWID")
ESPN_S2 = os.environ.get("ESPN_S2")

if not SWID or not ESPN_S2:
    raise RuntimeError(
        "SWID and ESPN_S2 must be set in a .env file (see .env.example). "
        "Get fresh values by logging into fantasy.espn.com and copying "
        "the SWID and espn_s2 cookies from your browser's devtools."
    )

OUTPUT_DIRECTORY = "output"

DATABASE_NAME = "espn_league.db"

REQUEST_TIMEOUT = 30
