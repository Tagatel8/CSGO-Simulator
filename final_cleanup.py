#!/usr/bin/env python3
"""
Properly clean up all duplicate players
"""
import sqlite3

def cleanup_all_duplicates():
    """Remove all duplicate player entries, keeping only one per player-team combination"""
    conn = sqlite3.connect('cs2_simulator.db')
    cursor = conn.cursor()

    try:
        # First, drop the existing index if it exists
        cursor.execute('DROP INDEX IF EXISTS idx_players_name_team')

        # Create a temporary table with unique entries
        cursor.execute('''
            CREATE TABLE players_temp AS
            SELECT MIN(id) as id, name, rating, team_id, role_id, is_career_player
            FROM players
            GROUP BY name, team_id
        ''')

        # Delete all from original table
        cursor.execute('DELETE FROM players')

        # Copy back from temp table
        cursor.execute('''
            INSERT INTO players (id, name, rating, team_id, role_id, is_career_player)
            SELECT id, name, rating, team_id, role_id, is_career_player
            FROM players_temp
        ''')

        # Drop temp table
        cursor.execute('DROP TABLE players_temp')

        # Recreate the unique index
        cursor.execute('CREATE UNIQUE INDEX idx_players_name_team ON players(name, team_id)')

        # Reset auto-increment counter
        cursor.execute('''
            UPDATE sqlite_sequence
            SET seq = (SELECT MAX(id) FROM players)
            WHERE name = 'players'
        ''')

        conn.commit()

        # Check results
        cursor.execute('SELECT COUNT(*) FROM players')
        final_count = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(DISTINCT name || team_id) FROM players')
        unique_combos = cursor.fetchone()[0]

        print(f"Cleanup complete!")
        print(f"Final player count: {final_count}")
        print(f"Unique player-team combinations: {unique_combos}")

        if final_count == unique_combos:
            print("✅ All duplicates removed successfully!")
        else:
            print("❌ Still have duplicates!")

    except Exception as e:
        print(f"Error during cleanup: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    cleanup_all_duplicates()