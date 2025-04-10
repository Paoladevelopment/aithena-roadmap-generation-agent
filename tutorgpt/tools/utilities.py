import psycopg2

from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool

from tutorgpt.utils.config import settings

@tool
def fetch_user_information(config: RunnableConfig) -> list[dict]:
    """Fetches user information from the database given a user_id."""
    configuration = config.get("configurable", {})
    user_id = configuration.get("user_id", None)
    
    if not user_id:
        raise ValueError("No user ID configured.")
    
    conn = None
    cursor = None

    try:
        conn = psycopg2.connect(settings.DATABASE_URI)
        cursor = conn.cursor()

        query = '''
            SELECT name, username, email
            FROM users 
            WHERE user_id = %s
        '''

        cursor.execute(query, (user_id,))

        rows = cursor.fetchall()
        column_names = [column[0] for column in cursor.description]
        results = [dict(zip(column_names, row)) for row in rows]

        cursor.close()
        conn.close()

        return results
    
    except psycopg2.Error as e:
        print(f"[DB ERROR] Failed to fetch user info: {e}")
        return []
    
    finally:
        try:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        except Exception as close_err:
            print(f"[DB WARNING] Error closing DB resources: {close_err}")

