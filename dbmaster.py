import mysql.connector
from typing import List, Tuple, Dict, Optional
import error_handler


class DbMaster:
    """
    A class to handle database operations with MySQL using mysql.connector.
    This class includes robust error handling, validation, and proper resource management.
    """

    def __init__(self, host: str, user: str, password: str, database: str):
        """
        Initializes the DbMaster object and establishes the connection to the MySQL database.

        Args:
            host (str): The hostname or IP address of the MySQL server.
            user (str): The username for the MySQL server.
            password (str): The password for the MySQL server.
            database (str): The name of the database to connect to.

        Raises:
            RuntimeError: If the connection to the database fails.
        """
        try:
            self.connection = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database
            )
            if not self.connection.is_connected():
                raise RuntimeError("Failed to establish a database connection.")
            self.cursor = self.connection.cursor(dictionary=True)
        except mysql.connector.Error as e:
            if self.connection:
                self.connection.close()
            self.connection = None
            self.cursor = None
            error_handler.handle_error_with_recommendation("Database Error", str(e))
            raise RuntimeError(f"Error connecting to MySQL: {e}")

    def execute_query(self, query: str, params: Optional[Tuple] = None) -> List[Dict]:
        """
        Executes an SQL query and fetches the result.

        Args:
            query (str): The SQL query to execute.
            params (Optional[Tuple]): The tuple of parameters to safely insert into the query.

        Returns:
            List[Dict]: A list of dictionaries containing the query results.

        Raises:
            RuntimeError: If no database connection is available or if an error occurs while executing the query.
            ValueError: If parameters are not provided in the correct format (tuple).
        """
        if not self.connection or not self.connection.is_connected():
            raise RuntimeError("No database connection.")
        if params and not isinstance(params, tuple):
            raise ValueError("Params must be a tuple")
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except mysql.connector.Error as e:
            error_handler.handle_error_with_recommendation("Database Error", str(e))
            raise RuntimeError(f"Error executing query: {e}")

    def insert_query_log(self, type_query: str, text_query: str) -> None:
        """
        Inserts or updates a database entry for tracking frequently executed queries.

        Increments the count for a query if it already exists (using ON DUPLICATE KEY UPDATE).

        Args:
            type_query (str): The type of the query (e.g., 'SELECT', 'INSERT').
            text_query (str): The text of the query.

        Raises:
            RuntimeError: If no database connection is available or if an error occurs during insertion.
        """
        if not self.connection or not self.connection.is_connected():
            raise RuntimeError("No database connection.")
        query = '''
            INSERT INTO popular_query (type_query, text_query) 
            VALUES (%s, %s) 
            ON DUPLICATE KEY UPDATE count = count + 1
        '''
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, (type_query, text_query))
            self.connection.commit()
        except mysql.connector.Error as e:
            self.connection.rollback()
            error_handler.handle_error_with_recommendation("Database Error", str(e))
            raise RuntimeError(f"Error inserting query log: {e}, transaction rolled back")

    def close(self) -> None:
        """
        Closes the database connection and cursor if they are active.

        Ensures all active resources are properly released to avoid resource leaks.
        """
        if self.cursor:
            self.cursor.close()
        if self.connection and self.connection.is_connected():
            self.connection.close()
