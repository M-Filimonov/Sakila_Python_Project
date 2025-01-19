import mysql.connector
from typing import List, Tuple, Dict, Optional
import error_handler


class DbMaster:
    """
    A class to handle database operations with MySQL using mysql.connector.
    Includes robust error handling, validation, and proper resource management.
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
        self.connection = None
        self.cursor = None
        try:
            self.connection = mysql.connector.connect(
                host=host, user=user, password=password, database=database, autocommit=False
            )
            if not self.connection.is_connected():
                raise RuntimeError("Failed to establish a database connection.")
            self.cursor = self.connection.cursor(dictionary=True)
        except mysql.connector.Error as e:
            if self.connection and self.connection.is_connected():
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
            raise ValueError("Params must be a tuple.")
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

        # Ensure the table exists
        if not self.check_db_table("popular_query"):
            create_table_query = '''
                CREATE TABLE IF NOT EXISTS popular_query (
                    log_id INT AUTO_INCREMENT PRIMARY KEY,
                    type_query VARCHAR(50) NOT NULL,
                    text_query VARCHAR(50) NOT NULL,
                    count INT DEFAULT 1,
                    query_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE INDEX unique_query (type_query, text_query)
                );
            '''
            try:
                self.cursor.execute(create_table_query)
                self.connection.commit()
            except mysql.connector.Error as e:
                self.connection.rollback()
                error_handler.handle_error_with_recommendation("Database Error", str(e))
                raise RuntimeError(f"Error creating 'popular_query' table: {e}")

        # Insert or update query log
        insert_query = '''
            INSERT INTO popular_query (type_query, text_query)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE count = count + 1
        '''
        try:
            self.cursor.execute(insert_query, (type_query, text_query))
            self.connection.commit()
        except mysql.connector.Error as e:
            self.connection.rollback()
            error_handler.handle_error_with_recommendation("Database Error", str(e))
            raise RuntimeError(f"Error inserting query log: {e}")

    def check_db_table(self, table_name: str) -> bool:
        """
        Checks if a table with the given name exists in the current database.

        Args:
            table_name (str): The name of the table to check.

        Returns:
            bool: True if the table exists, False otherwise.

        Raises:
            RuntimeError: If no database connection is available or if an error occurs during the query.
        """
        query = '''
            SELECT COUNT(*) AS table_exists
            FROM information_schema.tables
            WHERE table_schema = DATABASE() AND table_name = %s;
        '''
        try:
            self.cursor.execute(query, (table_name,))
            result = self.cursor.fetchone()
            return bool(result and result.get("table_exists", 0))  # Safely handle result and key lookup
        except mysql.connector.Error as e:
            error_handler.handle_error_with_recommendation("Database Error", str(e))
            raise RuntimeError(f"Error checking table existence: {e}")

    def close(self) -> None:
        """
        Closes the database connection and cursor if they are active.

        Ensures all active resources are properly released to avoid resource leaks.
        """
        try:
            if self.cursor:
                self.cursor.close()
        except Exception as e:
            error_handler.handle_error_with_recommendation("Cursor Close Error", str(e))
        try:
            if self.connection and self.connection.is_connected():
                self.connection.close()
        except Exception as e:
            error_handler.handle_error_with_recommendation("Connection Close Error", str(e))
