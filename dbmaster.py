import mysql.connector
from typing import List, Tuple, Dict, Optional
from error_handler import handle_error_with_recommendation

class DbMaster:
    def __init__(self, host: str, user: str, password: str, database: str):
        try:
            self.connection = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database
            )
            self.cursor = self.connection.cursor(dictionary=True)
        except mysql.connector.Error as e:
            self.connection = None
            self.cursor = None
            handle_error_with_recommendation("Database Error", str(e))
            raise RuntimeError(f"Error connecting to MySQL: {e}")

    def execute_query(self, query: str, params: Optional[Tuple] = None) -> List[Dict]:
        if not self.cursor:
            raise RuntimeError("No database connection.")
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except mysql.connector.Error as e:
            handle_error_with_recommendation("Database Error", str(e))
            raise RuntimeError(f"Error executing query: {e}")

    def insert_query_log(self, type_query: str, text_query: str) -> None:
        if not self.cursor:
            raise RuntimeError('No database connection')
        try:
            self.cursor.execute(
                '''
                INSERT INTO popular_query (type_query, text_query) 
                VALUES (%s, %s) 
                ON DUPLICATE KEY UPDATE count = count + 1
                ''', (type_query, text_query)
            )
            self.connection.commit()
        except mysql.connector.Error as e:
            self.connection.rollback()
            handle_error_with_recommendation("Database Error", str(e))
            raise RuntimeError(f'Error inserting query log: {e}, transactions have been rolled back')

    def close(self) -> None:
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
