import pyodbc

def get_connection():
    try:
        conn = pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=103.171.180.23;"        # Remote IP
            "DATABASE=CEO_DASH;"            # Database name
            "UID=CEO_DASH;"                 # SQL login
            "PWD=P_?2TGuw1czpvk8f;"       # <-- put password here
            "TrustServerCertificate=yes;"
        )
        
        return conn

    except Exception as e:
        print("❌ SQL Server connection error:", e)
        return None
