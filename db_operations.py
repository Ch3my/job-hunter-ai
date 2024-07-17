from datetime import datetime
import sqlite3

def create_table(conn):
    # conn = sqlite3.connect('jobs.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS jobs (
        title TEXT,
        company TEXT,
        description TEXT,
        joburl TEXT,
        applied TEXT,
        createdAt TEXT,
        PRIMARY KEY (title, company)
    )
    ''')
    conn.commit()

def insert_job(conn, job):
    current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor = conn.cursor()
    try:
        cursor.execute('''
        INSERT INTO jobs (title, company, description, joburl, applied, createdAt)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (job['title'], job['companyName'], job['jobDescription'], job['jobPostingUrl'], 'Not applied', current_date))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # Job already exists in the database
        return False