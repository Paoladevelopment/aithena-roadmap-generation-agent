import psycopg2

from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool

from tutorgpt.utils.config import settings

@tool
def fetch_user_information(config: RunnableConfig) -> dict:
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
            SELECT name, username, email, user_id
            FROM users 
            WHERE user_id = %s
        '''

        cursor.execute(query, (user_id,))

        row = cursor.fetchone()
        
        if row:
            column_names = [column[0] for column in cursor.description]
            user_data = dict(zip(column_names, row))

            cursor.close()
            conn.close()
            
            return user_data
        else:
            cursor.close()
            conn.close()

            return {
                "name": "Unknown User",
                "username": "unknown_user",
                "email": "unknown@example.com",
                "user_id": "unknown_user_id"
            }
    
    except psycopg2.Error as e:
        return {
            "name": "Unknown User",
            "username": "unknown_user",
            "email": "unknown@example.com",
            "user_id": "unknown_user_id"
        }
    
    finally:
        try:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        except Exception:
            pass

