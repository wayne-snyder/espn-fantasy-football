"""
Runs every analytics report in dependency order.

Order matters: several reports build on tables that earlier scripts
create (auction_features -> manager_features -> manager_profiles ->
auction_strategy), so this isn't just an arbitrary list.
"""

import build_auction_features
import build_manager_data
import draft_value
import enrich_manager_features
import lineup_efficiency
import luck_index
import manager_profiles
import optimal_lineup
import position_personality
import position_spending
import power_rankings

import auction_personality
import auction_strategy

# Order matters — later reports depend on tables built by earlier ones
REPORTS = [
    # Independent, feed nothing else
    draft_value,
    lineup_efficiency,
    optimal_lineup,
    position_spending,
    position_personality,
    power_rankings,
    luck_index,
    build_manager_data,       # -> manager_history

    # Manager-personality pipeline (order-dependent)
    build_auction_features,   # -> auction_features
    enrich_manager_features,  # auction_features -> manager_features
    manager_profiles,         # manager_features -> manager_profiles
    auction_personality,      # auction_features -> manager_personality_career.csv
    auction_strategy,         # manager_profiles -> auction_strategy.csv
]


def main():
    for report in REPORTS:
        print()
        print("=" * 60)
        print(report.__name__)
        print("=" * 60)
        report.main()


if __name__ == "__main__":
    main()
