import os
import json
import mysql.connector
from mysql.connector import Error


class TranscriptsDB:
    def __init__(self):
        self.host = os.getenv('DB_HOST')
        self.user = os.getenv('DB_USER')
        self.password = os.getenv('DB_PASSWORD')
        self.database = os.getenv('DB_NAME')
        self.connection = None
        print("Environment variables loaded")

    def __enter__(self):
        print("Connecting to the database...")
        self.connection = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database,
            connection_timeout=10
        )
        print("Connected to the database")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection is not None and self.connection.is_connected():
            self.connection.close()

    def create_table(self, table_name, column_name):
        try:
            with self.connection.cursor() as cursor:
                # Check if the table exists
                cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
                table_exists = cursor.fetchone()

                if table_exists:
                    # Check if the column exists
                    cursor.execute(
                        f"SHOW COLUMNS FROM {table_name} LIKE '{column_name}'")
                    column_exists = cursor.fetchone()

                    if not column_exists:
                        # Add the new column
                        cursor.execute(
                            f"ALTER TABLE {table_name} ADD COLUMN {column_name} TEXT")
                else:
                    # Create the table with the specified column
                    cursor.execute(
                        f"CREATE TABLE {table_name} (session_id VARCHAR(255) PRIMARY KEY, {column_name} TEXT)")

                self.connection.commit()
        except Error as e:
            print(f"The error '{e}' occurred")

    def store_data(self, table_name, session_id, column_name, value):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(f"INSERT INTO {table_name} (session_id, {column_name}) VALUES (%s, %s) ON DUPLICATE KEY UPDATE {column_name}=%s",
                               (session_id, json.dumps(value, ensure_ascii=False), json.dumps(value, ensure_ascii=False)))
                self.connection.commit()
        except Error as e:
            print(f"The error '{e}' occurred")

    def retrieve_data(self, table_name, session_id, column_name):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    f"SELECT {column_name} FROM {table_name} WHERE session_id=%s", (session_id,))
                result = cursor.fetchone()

                if result and result[0]:
                    return json.loads(result[0])
                else:
                    return None
        except Error as e:
            print(f"The error '{e}' occurred")

    def clear_data(self, table_name, session_id, column_name):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    f"UPDATE {table_name} SET {column_name} = '[]' WHERE session_id=%s", (session_id,))
                self.connection.commit()
        except Error as e:
            print(f"The error '{e}' occurred")
