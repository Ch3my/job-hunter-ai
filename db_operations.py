from datetime import datetime
import sqlite3

# Cada funcion crea su conexion, entonces no hay problema si la llaman de otro thread
# porque crearia su propia conexion en su propio thread

# Default Behavior (check_same_thread=True):
# SQLite connections can only be used by the thread that created them.
# If you try to use the connection from a different thread, you'll get a 
# sqlite3.ProgrammingError: SQLite objects created in a thread can only be used in that same thread.
def create_connection():
    return sqlite3.connect("jobs.db", check_same_thread=True)

def truncate_table():
    conn = create_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM jobs")
        conn.commit()
        return True, "La tabla de trabajos ha sido vaciada exitosamente."
    except sqlite3.Error as e:
        return False, f"Ocurrió un error al vaciar la tabla de trabajos: {str(e)}"
    finally:
        if conn:
            conn.close()

def create_table():
    conn = create_connection()
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
    conn.close()

def insert_job(job):
    conn = create_connection()
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
    finally:
        if conn:
            conn.close()

def update_job_status(new_status, title, company):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE jobs SET applied=? WHERE title=? AND company=?", (new_status, title, company))
    conn.commit()
    conn.close()

def select_jobs():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT title, company, applied, createdAt FROM jobs order by createdAt desc")
    rows = cursor.fetchall()
    conn.close()
    return rows

def check_table_exists():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='jobs'")
    table_exists = cursor.fetchone()
    conn.close()
    return table_exists