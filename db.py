import pyodbc

pyodbc.pooling = True  # ✅ enable connection pooling

def get_connection():
    return pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=103.171.180.23;"
        "DATABASE=CEO_DASH;"
        "UID=CEO_DASH;"
        "PWD=P_?2TGuw1czpvk8f;"
        "TrustServerCertificate=yes;"
    )

      