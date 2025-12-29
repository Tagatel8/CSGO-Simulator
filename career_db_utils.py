def delete_career_file(career_name: str, db_folder: str = '.') -> bool:
    """
    Deletes the career database file for the given career name.
    Returns True if deleted, False if not found.
    """
    safe_name = career_name.replace(' ', '_')
    db_name = f"career_{safe_name}.db"
    db_path = os.path.join(db_folder, db_name)
    if os.path.exists(db_path):
        os.remove(db_path)
        return True
    return False
import shutil
import os

def create_career_database(career_name: str, base_db_path: str = 'cs2_simulator.db', db_folder: str = '.') -> str:
    """
    Copies the base database and renames it for the career save.
    Returns the path to the new career database.
    """
    safe_name = career_name.replace(' ', '_')
    new_db_name = f"career_{safe_name}.db"
    new_db_path = os.path.join(db_folder, new_db_name)
    shutil.copy2(base_db_path, new_db_path)

    # Clean up career_players, careers and career_matches tables in the new DB
    import sqlite3
    conn = sqlite3.connect(new_db_path)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM career_players')
    cursor.execute('DELETE FROM careers')
    cursor.execute('DELETE FROM career_matches')
    conn.commit()
    conn.close()
    return new_db_path

# Example usage:
# new_db = create_career_database('My Career Save')
# print(f"Created career DB at: {new_db}")
