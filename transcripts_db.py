import json
import mysql.connector
from mysql.connector import Error


class TranscriptsDB:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None

    def __enter__(self):
        self.connection = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection is not None and self.connection.is_connected():
            self.connection.close()

    def create_table(self):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute('''CREATE TABLE IF NOT EXISTS conversation
                                  (session_id VARCHAR(36) PRIMARY KEY, transcript_history TEXT)''')
                self.connection.commit()
        except Error as e:
            print(f"The error '{e}' occurred")

    def store_transcript_history(self, session_id, transcript_history):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("INSERT INTO conversation (session_id, transcript_history) VALUES (%s, %s) ON DUPLICATE KEY UPDATE transcript_history=%s",
                               (session_id, json.dumps(transcript_history, ensure_ascii=False), json.dumps(transcript_history, ensure_ascii=False)))
                self.connection.commit()
        except Error as e:
            print(f"The error '{e}' occurred")

    def retrieve_transcript_history(self, session_id):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    "SELECT transcript_history FROM conversation WHERE session_id=%s", (session_id,))
                result = cursor.fetchone()

                if result:
                    return json.loads(result[0])
                else:
                    return None
        except Error as e:
            print(f"The error '{e}' occurred")

    def clear_transcript_history(self, session_id):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE conversation SET transcript_history = '[]' WHERE session_id=%s", (session_id,))
                self.connection.commit()
        except Error as e:
            print(f"The error '{e}' occurred")
