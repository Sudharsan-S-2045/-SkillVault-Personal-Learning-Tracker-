import sqlite3
from datetime import datetime
from functools import reduce
from collections import defaultdict

class Skill:
    """
    Represents a learning skill with associated metadata.
    Attributes:
        id (int): Unique identifier for the skill.
        name (str): Name of the skill.
        category (str): Category of the skill (e.g., Tech, Creative).
        target_hours (int): Goal for hours to practice.
    """
    def __init__(self, id, name, category, target_hours):
        self.id = id
        self.name = name
        self.category = category
        self.target_hours = target_hours

class PracticeSession:
    """
    Represents a practice session for a specific skill.
    Attributes:
        id (int): Unique identifier for the session.
        skill_id (int): Foreign key to Skill.
        duration_minutes (int): Duration of the session.
        notes (str): Notes about the session.
        date (str): Date of the session (YYYY-MM-DD).
    """
    def __init__(self, id, skill_id, duration_minutes, notes, date):
        self.id = id
        self.skill_id = skill_id
        self.duration_minutes = duration_minutes
        self.notes = notes
        self.date = date

class SkillDatabase:
    """
    Handles all database interactions including skill and session storage and queries.
    """
    def __init__(self, db_name='skillvault.db'):
        try:
            

            self.conn = sqlite3.connect(db_name)

            self.create_tables()
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")

    def create_tables(self):
        """Creates the skills and sessions tables in the database if not exists."""
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS skills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                target_hours INTEGER NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                skill_id INTEGER,
                duration_minutes INTEGER,
                notes TEXT,
                date TEXT,
                FOREIGN KEY(skill_id) REFERENCES skills(id)
            )
        ''')
        self.conn.commit()

    def add_skill(self, skill: Skill):
        """Adds a new skill to the database."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO skills (name, category, target_hours) VALUES (?, ?, ?)",
                        (skill.name, skill.category, skill.target_hours))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Failed to add skill: {e}")

    def log_session(self, session: PracticeSession):
        """Logs a new practice session."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO sessions (skill_id, duration_minutes, notes, date) VALUES (?, ?, ?, ?)",
                        (session.skill_id, session.duration_minutes, session.notes, session.date))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Failed to log session: {e}")

    def get_progress(self):
        """Returns progress statistics for all skills."""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT s.id, s.name, s.target_hours, IFNULL(SUM(sess.duration_minutes), 0)/60.0 AS total_hours
            FROM skills s
            LEFT JOIN sessions sess ON s.id = sess.skill_id
            GROUP BY s.id
        ''')
        rows = cursor.fetchall()
        return list(map(lambda r: {
            'Skill': r[1],
            'Target Hours': r[2],
            'Total Practiced': round(r[3], 2),
            'Progress %': round((r[3] / r[2]) * 100, 2) if r[2] else 0
        }, rows))

    def delete_skill(self, skill_id):
        """Deletes a skill and its associated sessions."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM sessions WHERE skill_id=?", (skill_id,))
            cursor.execute("DELETE FROM skills WHERE id=?", (skill_id,))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Failed to delete skill: {e}")

class SkillTracker:
    """
    Command-line interface for interacting with the skill tracker system.
    """
    def __init__(self):
        self.db = SkillDatabase()

    def run(self):
        while True:
            print("\nSkillVault Menu:")
            print("1. Add a New Skill")
            print("2. Log Practice Session")
            print("3. View Progress")
            print("4. Delete Skill")
            print("5. Exit")
            choice = input("Choose an option: ")

            if choice == '1':
                try:
                    name = input("Skill Name: ")
                    category = input("Category (Tech, Creative, etc.): ")
                    target_hours = int(input("Target Hours: "))
                    self.db.add_skill(Skill(None, name, category, target_hours))
                except ValueError:
                    print("Invalid input for target hours.")

            elif choice == '2':
                try:
                    skill_id = int(input("Skill ID: "))
                    duration = int(input("Duration (in minutes): "))
                    notes = input("Notes: ")
                    date = input("Date (YYYY-MM-DD): ") or datetime.now().strftime('%Y-%m-%d')
                    self.db.log_session(PracticeSession(None, skill_id, duration, notes, date))
                except ValueError:
                    print("Invalid input. Please enter numbers where required.")

            elif choice == '3':
                progress = self.db.get_progress()
                for p in progress:
                    print(f"Skill: {p['Skill']}, Target: {p['Target Hours']} hrs, Practiced: {p['Total Practiced']} hrs, Progress: {p['Progress %']}%")

            elif choice == '4':
                try:
                    skill_id = int(input("Enter Skill ID to delete: "))
                    self.db.delete_skill(skill_id)
                except ValueError:
                    print("Invalid skill ID.")

            elif choice == '5':
                break
            else:
                print("Invalid choice.")

if __name__ == '__main__':
    tracker = SkillTracker()
    tracker.run()
