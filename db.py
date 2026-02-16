# db.py
import psycopg2
from psycopg2.extras import RealDictCursor

def get_connection():
    try:
        conn = psycopg2.connect(
            host="localhost",             # your PostgreSQL host
            database="driving_school_hr", # <-- correct database name
            user="postgres",              # your DB user
            password="Test@123",     # your DB password
            port=5432                     # default PostgreSQL port
        )
        return conn
    except Exception as e:
        print("Error connecting to PostgreSQL:", e)
        return None
