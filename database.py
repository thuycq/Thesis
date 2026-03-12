import sqlite3
import os

DB_PATH = "data/kltn.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():

    os.makedirs("data", exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # USERS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT,
        lecturer_id INTEGER
    )
    """)

    # LECTURERS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS lecturers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lecturer_code TEXT,
        full_name TEXT,
        email TEXT,
        department TEXT
    )
    """)

    # BCTT
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bctt_students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mssv TEXT,
        full_name TEXT,
        class_name TEXT,
        gvhd_id INTEGER
    )
    """)

    # KLTN
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS kltn_students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mssv TEXT,
        full_name TEXT,
        class_name TEXT,
        gvhd_id INTEGER,
        gvpb_id INTEGER,
        cthd_id INTEGER,
        tvhd_id INTEGER,
        tkhd_id INTEGER,
        defense_time TEXT,
        room TEXT,
        council TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mssv TEXT UNIQUE,
        full_name TEXT,
        class_name TEXT,
        gvhd_id INTEGER,
        project_type TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS kltn_details (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER UNIQUE,
        gvpb_id INTEGER,
        cthd_id INTEGER,
        tvhd_id INTEGER,
        tkhd_id INTEGER,
        defense_time TEXT,
        room TEXT,
        council TEXT
    )
    """)

    conn.commit()
    conn.close()


def upgrade_students_table():

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    columns_to_add = [
        ("topic_title", "TEXT"),
        ("report_link", "TEXT"),
        ("turnitin_link", "TEXT"),
        ("bctt_language", "TEXT"),
        ("kltn_language", "TEXT"),
        ("score_bctt", "REAL"),
        ("score_gvhd", "REAL"),
        ("score_gvpb", "REAL"),
        ("score_cthd", "REAL"),
        ("score_tvhd", "REAL"),
        ("score_tkhd", "REAL")
    ]

    for column_name, column_type in columns_to_add:
        try:
            cursor.execute(f"ALTER TABLE students ADD COLUMN {column_name} {column_type}")
        except sqlite3.OperationalError:
            pass

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    upgrade_students_table()