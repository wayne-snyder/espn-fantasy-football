import draft_value
import lineup_efficiency
import luck_index
import manager_spending
import optimal_lineup
import position_spending
import power_rankings

REPORTS = [
    draft_value,
    lineup_efficiency,
    optimal_lineup,
    manager_spending,
    position_spending,
    power_rankings,
    luck_index,
]


def main():
    for report in REPORTS:
        print()
        print("=" * 60)
        report.main()


if __name__ == "__main__":
    main()
