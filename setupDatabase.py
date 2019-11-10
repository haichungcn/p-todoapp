import sqlite3
import os
from datetime import datetime

DEFAULT_PATH = os.path.join(os.path.dirname(__file__), 'database.sqlite3')

conn = sqlite3.connect(DEFAULT_PATH)
cur = conn.cursor()

sql = """
    CREATE TABLE IF NOT EXISTS todos(
        id INTEGER PRIMARY KEY,
        body TEXT NOT NULL,
        status TEXT DEFAULT "undone",
        due_date DATE NOT NULL,
        project_id INTEGER,
        creator_id INTEGER,
        assigned_id INTEGER,
        timestamp DATE NOT NULL
    )
"""

sql_users = """
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY,
        user_name TEXT NOT NULL,
        user_email TEXT NOT NULL,
        user_password TEXT NOT NULL,
        birthday DATE,
        phone_number INTEGER,
        timestamp DATE NOT NULL
    )
"""

sql_projects = """
    CREATE TABLE IF NOT EXISTS projects(
        id INTEGER PRIMARY KEY,
        project_name TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT "unfinished",
        creator_id INTEGER NOT NULL,
        timestamp DATE NOT NULL
    )
"""

sql_project_users = """
    CREATE TABLE IF NOT EXISTS project_users(
        id INTEGER PRIMARY KEY,
        project_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL
    )
"""

sql_history = """
    CREATE TABLE IF NOT EXISTS history(
        id INTEGER PRIMARY KEY,
        action TEXT NOT NULL,
        table_name TEXT NOT NULL,
        row_id INTEGER NOT NULL,
        owner_id INTEGER NOT NULL,
        timestamp DATE NOT NULL
    )
"""

sql_default_user = """
    INSERT INTO users (
        user_name,
        user_email,
        user_password,
        birthday,
        phone_number,
        timestamp
    ) VALUES (
        "haict",
        "hai@hai.com",
        "123",
        "01/11/1987",
        "888999666",
        ?
    )
"""


look_for_user = """
    SELECT id, user_name FROM users WHERE user_name LIKE "haict"
"""

def setup():
    cur.execute(sql)
    cur.execute(sql_users)
    cur.execute(sql_projects)
    cur.execute(sql_project_users)
    cur.execute(sql_history)

    cur.execute(look_for_user)
    result = cur.fetchall()
    
    if not result:
        time = datetime.now()
        cur.execute(sql_default_user, (time,))
    
    cur.execute(look_for_user)
    result = cur.fetchall()

    conn.commit()

    return(result[0])