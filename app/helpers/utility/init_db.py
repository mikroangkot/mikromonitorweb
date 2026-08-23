import sqlite3


async def init_db():
    with sqlite3.connect("project.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
			CREATE TABLE IF NOT EXISTS user_activities(
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				app_name TEXT,
				username TEXT,
				last_activity TEXT,
				ip_address TEXT,
				lat_long TEXT,
				is_synced INTEGER DEFAULT 0,
				datetime_created TIMESTAMP DEFAULT (datetime('now', 'localtime'))
			)
		""")
        conn.commit()