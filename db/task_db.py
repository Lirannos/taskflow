import sqlite3
from datetime import datetime

class TaskDB:
    DATABASE = 'gta.db'  # SQLite database file

    def get_db_connection(self):
        # Establish and return a connection to the SQLite database
        conn = sqlite3.connect(self.DATABASE)
        conn.row_factory = sqlite3.Row  # Allows accessing columns by name
        return conn

    def create_table(self):
        # Creates the 'tasks' table if it doesn't exist already
        conn = self.get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                priority TEXT,
                day TEXT,
                time TEXT,
                duration INTEGER,
                status TEXT DEFAULT 'pending',
                user_id INTEGER NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

    def add_task(self, title, description, priority, day, time, duration, user_id):
        # Inserts a new task into the tasks table
        conn = self.get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO tasks (title, description, priority, day, time, duration, user_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (title, description, priority, day, time, duration, user_id))
        conn.commit()
        task_id = cursor.lastrowid  # 🔥 קריטי: שמירת ה-ID שנוצר
        conn.close()
        return task_id

    def delete_task(self, task_id, user_id):
        # Deletes a task by ID and user ID to ensure ownership
        conn = self.get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM tasks WHERE id = ? AND user_id = ?', (task_id, user_id))
        conn.commit()
        conn.close()

    def get_list_of_tasks(self, user_id):
        # Retrieves all tasks for a given user as SQLite Row objects
        conn = self.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE user_id = ?", (user_id,))
        tasks = cursor.fetchall()
        conn.close()
        return tasks

    def get_tasks_json(self, user_id):
        # Retrieves all tasks for a user and returns them as a list of dictionaries
        conn = self.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE user_id = ?", (user_id,))
        tasks = cursor.fetchall()
        tasks_list = [self.row_to_dict(row) for row in tasks]
        conn.close()
        return tasks_list

    def get_tasks_by_day_and_time(self, user_id, day, time):
        """
        Retrieves tasks that overlap with the given day and time for a given user.
        This includes tasks that started earlier and span across the given time.
        """
        conn = self.get_db_connection()
        cursor = conn.cursor()

        # Parse the given time to extract hour as integer
        try:
            target_hour = int(datetime.strptime(time, "%H:%M").strftime("%H"))
        except ValueError:
            target_hour = int(time.split(":")[0])  # fallback if formatting fails

        # Fetch all tasks on that day for the user
        cursor.execute('SELECT * FROM tasks WHERE day = ? AND user_id = ?', (day, user_id))
        all_tasks = cursor.fetchall()

        overlapping_tasks = []

        for row in all_tasks:
            start_time = row["time"]
            duration = int(row["duration"])

            try:
                start_hour = int(datetime.strptime(start_time, "%H:%M").strftime("%H"))
            except ValueError:
                start_hour = int(start_time.split(":")[0])

            if target_hour in range(start_hour, start_hour + duration):
                overlapping_tasks.append(self.row_to_dict(row))

        conn.close()
        return overlapping_tasks

    def row_to_dict(self, row):
        # Helper method to convert SQLite Row to dictionary
        return {
            "id": row["id"],
            "title": row["title"],
            "description": row["description"],
            "priority": row["priority"],
            "day": row["day"],
            "time": row["time"],
            "duration": row["duration"]
        }
    
    def get_task_by_id(self, task_id, user_id):
        """Fetch a specific task by its ID and user."""
        conn = self.get_db_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM tasks WHERE id = ? AND user_id = ?",
            (task_id, user_id)
    )
        task = cursor.fetchone()
        conn.close()

        if task:
            return {
                "id": task["id"],
                "title": task["title"],
                "description": task["description"],
                "priority": task["priority"],
                "day": task["day"],
                "time": task["time"],
                "duration": task["duration"],
                "user_id": task["user_id"]
            }
        return None

