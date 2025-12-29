#!/usr/bin/env python3
"""
CS2 Roles Demo - Show player roles in teams
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cs2_database import CS2Database

def main():
    print("🎭 CS2 Player Roles Demonstration")
    print("=" * 40)

    db = CS2Database()
    teams = db.get_teams_dict()

    # Show role distribution in top teams
    top_teams = ["Vitality", "G2", "FaZe", "Natus Vincere", "Astralis"]

    for team_name in top_teams:
        if team_name in teams:
            print(f"\n🏆 {team_name} Roster:")
            role_count = {}

            for player in teams[team_name]:
                role = player.get('role', 'Unknown')
                role_icon = player.get('role_icon', '❓')
                role_count[role] = role_count.get(role, 0) + 1

                print(f"  {role_icon} {player['name']} ({player['rating']}) - {role}")

            print(f"  📊 Role Distribution: {role_count}")

    # Show role statistics
    print("\n📈 Role Statistics Across All Teams:")
    all_roles = {}
    total_players = 0

    for team_name, players in teams.items():
        for player in players:
            role = player.get('role', 'Unknown')
            all_roles[role] = all_roles.get(role, 0) + 1
            total_players += 1

    for role, count in sorted(all_roles.items()):
        percentage = (count / total_players * 100) if total_players > 0 else 0
        print(f"{role}: {count} ({percentage:.1f}%)")

    print("\n🔄 Future Transfer Possibilities:")
    print("  • Teams can search for 'AWPer' replacements")
    print("  • Balanced rosters require specific role ratios")
    print("  • Young players can specialize in specific roles")
    print("  • Transfer fees based on role scarcity")

if __name__ == "__main__":
    main()