#!/usr/bin/env python3
"""
Reset and reassign player roles with realistic distribution
"""
import sqlite3
import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cs2_database import CS2Database

def reset_roles():
    """Reset all player roles and reassign them realistically"""
    db = CS2Database()

    try:
        conn = db.get_connection()
        cursor = conn.cursor()

        # Clear existing role assignments
        print("Clearing existing role assignments...")
        cursor.execute('UPDATE players SET role_id = NULL')

        # Re-run the migration logic
        print("Reassigning roles with realistic distribution...")

        # Get all players without roles
        cursor.execute('SELECT id, name FROM players WHERE role_id IS NULL')
        players_to_update = cursor.fetchall()

        # Get team counts
        cursor.execute('SELECT team_id, COUNT(*) as player_count FROM players WHERE role_id IS NULL GROUP BY team_id')
        team_counts = dict(cursor.fetchall())

        # Assign roles using the new algorithm
        role_assignments = db.assign_realistic_roles(players_to_update, team_counts)

        # Update the database
        for player_id, player_name in players_to_update:
            role_name = role_assignments.get(player_id, "Rifler")
            cursor.execute('SELECT id FROM roles WHERE name = ?', (role_name,))
            role_row = cursor.fetchone()
            role_id = role_row[0] if role_row else 2  # Default to Rifler

            cursor.execute('UPDATE players SET role_id = ? WHERE id = ?', (role_id, player_id))

        conn.commit()
        print(f"Successfully reassigned roles to {len(players_to_update)} players")

        # Show new distribution
        cursor.execute('''
            SELECT r.name, COUNT(*) as count
            FROM players p
            JOIN roles r ON p.role_id = r.id
            GROUP BY r.name
            ORDER BY count DESC
        ''')

        print("\n📊 New Role Distribution:")
        total_players = 0
        results = cursor.fetchall()
        for role_name, count in results:
            total_players += count

        for role_name, count in results:
            percentage = (count / total_players * 100) if total_players > 0 else 0
            print(f"  {role_name}: {count} ({percentage:.1f}%)")

        print(f"\nTotal players: {total_players}")

    except Exception as e:
        print(f"Error resetting roles: {e}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    reset_roles()