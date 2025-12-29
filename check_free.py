#!/usr/bin/env python3
"""
Check Free Agent players
"""
import sqlite3

def check_free_agents():
    conn = sqlite3.connect('cs2_simulator.db')
    cursor = conn.cursor()

    # Check specific player
    cursor.execute('''
        SELECT t.name, COUNT(*) as count
        FROM players p
        JOIN teams t ON p.team_id = t.id
        WHERE p.name = '910'
        GROUP BY t.name
    ''')

    print("Teams for player '910':")
    for row in cursor.fetchall():
        team, count = row
        print(f"  {team}: {count} times")

    # Check all players that appear multiple times
    cursor.execute('''
        SELECT p.name, COUNT(*) as total_count,
               GROUP_CONCAT(t.name) as teams
        FROM players p
        JOIN teams t ON p.team_id = t.id
        GROUP BY p.name
        HAVING total_count > 1
        ORDER BY total_count DESC
        LIMIT 10
    ''')

    print("\nPlayers appearing on multiple teams:")
    for row in cursor.fetchall():
        name, count, teams = row
        print(f"  {name}: {count} times on teams: {teams}")

    conn.close()

if __name__ == "__main__":
    check_free_agents()