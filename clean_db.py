#!/usr/bin/env python3
"""
Clean up duplicate players in the database
"""
import sqlite3

def clean_duplicates():
    """Remove duplicate players, keeping only one entry per player per team"""
    conn = sqlite3.connect('cs2_simulator.db')
    cursor = conn.cursor()

    try:
        # First, let's see what we have
        cursor.execute('SELECT COUNT(*) FROM players')
        total_before = cursor.fetchone()[0]
        print(f"Total players before cleanup: {total_before}")

        # Find duplicates (players with same name and team_id)
        cursor.execute('''
            SELECT name, team_id, COUNT(*) as count
            FROM players
            GROUP BY name, team_id
            HAVING count > 1
            ORDER BY count DESC
        ''')

        duplicates = cursor.fetchall()
        print(f"Found {len(duplicates)} duplicate groups")

        # For each duplicate group, keep the first one and delete the rest
        for name, team_id, count in duplicates:
            # Get all IDs for this player/team combination
            cursor.execute('''
                SELECT id FROM players
                WHERE name = ? AND team_id = ?
                ORDER BY id
            ''', (name, team_id))

            ids = [row[0] for row in cursor.fetchall()]
            # Keep the first one, delete the rest
            ids_to_delete = ids[1:]

            if ids_to_delete:
                placeholders = ','.join('?' * len(ids_to_delete))
                cursor.execute(f'DELETE FROM players WHERE id IN ({placeholders})', ids_to_delete)
                print(f"Removed {len(ids_to_delete)} duplicates for {name} (team_id: {team_id})")

        # Now add unique constraint to prevent future duplicates
        print("Adding unique constraint...")
        cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_players_name_team ON players(name, team_id)')

        conn.commit()

        # Check results
        cursor.execute('SELECT COUNT(*) FROM players')
        total_after = cursor.fetchone()[0]
        print(f"Total players after cleanup: {total_after}")
        print(f"Removed {total_before - total_after} duplicate entries")

        # Verify no more duplicates
        cursor.execute('''
            SELECT COUNT(*) FROM (
                SELECT name, team_id, COUNT(*) as count
                FROM players
                GROUP BY name, team_id
                HAVING count > 1
            )
        ''')
        remaining_duplicates = cursor.fetchone()[0]
        print(f"Remaining duplicate groups: {remaining_duplicates}")

    except Exception as e:
        print(f"Error during cleanup: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    clean_duplicates()