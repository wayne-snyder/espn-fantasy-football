"""
Builds the auction_features table: one row per draft pick, enriched
with manager identity, budget context, and price-tier signals used by
downstream manager/personality reports (enrich_manager_features.py,
auction_personality.py).

This script was missing from the repo — the manager-personality reports
depend on a table (`auction_features`) and columns (`is_elite_purchase`,
`draft_phase`, `manager_id`, etc.) that nothing built. Reconstructed to
match the schema those downstream reports already expect. Thresholds
below (e.g. "elite" = top 15% priced) are reasonable defaults — tune
them if they don't match how your league actually plays out.

Input:
    auction_picks, teams, league_settings

Output:
    auction_features (table)
    auction_history_enriched.csv (report)
"""

import pandas as pd

from core.auction import build_auction_dataset
from core.features import build_auction_features as apply_core_features
from db_utils import load_table, save_report, save_table

# Purchase-order thresholds within a manager's own draft (by pick order,
# not clock time) that define "early/mid/late" phases
EARLY_PICK_CUTOFF = 5
MID_PICK_CUTOFF = 10

# league_price_percentile thresholds (rank of bid_amount within that
# season, 0-1) used for elite/value tagging and price tiers
ELITE_PERCENTILE = 0.85
MID_PERCENTILE = 0.40
VALUE_POSITION_PERCENTILE = 0.25


def add_manager_and_team_identity(picks, teams):

    team_info = teams.rename(
        columns={"team_id": "fantasy_team_id"}
    )[["season", "fantasy_team_id", "team_name", "owner"]]

    df = picks.merge(
        team_info, on=["season", "fantasy_team_id"], how="left"
    )

    df["team_id"] = df["fantasy_team_id"]
    df["manager_id"] = df["owner"]
    df = df.drop(columns=["owner"])

    return df


def add_budget_context(df, settings):

    df = df.merge(
        settings[["season", "auction_budget", "roster_size"]],
        on="season",
        how="left",
    )

    df["bid_pct_budget"] = (
        df["bid_amount"] / df["auction_budget"] * 100
    ).round(2)

    # Per-season core feature engineering needs the real budget/roster
    # size for that season, not a fixed default, so run season-by-season
    enriched_seasons = []

    for season, season_df in df.groupby("season"):

        budget = season_df["auction_budget"].iloc[0]
        roster_size = season_df["roster_size"].iloc[0]

        season_df = apply_core_features(season_df)
        # apply_core_features used its own default budget/roster_size
        # internally for remaining_budget/roster_slots; recompute those
        # two with the real per-season values instead
        season_df["remaining_budget"] = budget - season_df["running_spend"]
        season_df["remaining_roster_spots"] = (
            roster_size - season_df["players_bought"]
        )
        season_df["avg_dollars_per_open_slot"] = season_df[
            "remaining_budget"
        ] / season_df["remaining_roster_spots"].clip(lower=1)

        enriched_seasons.append(season_df)

    return pd.concat(enriched_seasons, ignore_index=True)


def add_purchase_number(df):
    """Overall pick order per manager per season (not per-position)."""

    df = df.sort_values(["season", "fantasy_team_id", "pick_number"])

    df["purchase_number"] = (
        df.groupby(["season", "fantasy_team_id"]).cumcount() + 1
    )

    return df


def add_phase_and_tier(df):

    df["draft_phase"] = df["purchase_number"].apply(
        lambda n: "early"
        if n <= EARLY_PICK_CUTOFF
        else ("mid" if n <= MID_PICK_CUTOFF else "late")
    )

    df["is_elite_purchase"] = df["league_price_percentile"] >= ELITE_PERCENTILE
    df["is_value_purchase"] = (
        df["position_price_percentile"] <= VALUE_POSITION_PERCENTILE
    )

    df["price_tier"] = df["league_price_percentile"].apply(
        lambda p: "Elite"
        if p >= ELITE_PERCENTILE
        else ("Mid-Tier" if p >= MID_PERCENTILE else "Value")
    )

    return df


def build(picks, teams, settings):

    df = add_manager_and_team_identity(picks, teams)
    df = add_budget_context(df, settings)
    df = add_purchase_number(df)
    df = build_auction_dataset(df)  # spend_share, price percentiles
    df = add_phase_and_tier(df)

    return df


def main():

    picks = load_table("auction_picks")
    teams = load_table("teams")
    settings = load_table("league_settings")

    features = build(picks, teams, settings)

    save_table(features, "auction_features")
    save_report(features, "auction_history_enriched.csv")

    print(f"Built auction_features ({len(features)} rows)")


if __name__ == "__main__":
    main()
