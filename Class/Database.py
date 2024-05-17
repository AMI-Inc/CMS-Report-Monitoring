import psycopg2
import base64
from . import Config

class Database:
    def __init__(self, 
                 host=Config.stage_host, 
                 database=Config.stage_database, 
                 user=Config.stage_user, 
                 password=Config.stage_password, 
                 port=Config.stage_port, 
                 client_encoding=Config.client_encoding
                ):

        self.dbname = database
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.connection = None
        self.cursor = None
        self.client_encoding = client_encoding
    def connect(self):
        try:
            self.connection = psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
                client_encoding = self.client_encoding
            )
            self.cursor = self.connection.cursor()
            print("Connected to the database.")
        except Exception as e:
            return f"Error: Unable to connect to the database - {e}"

    def disconnect(self):
        if self.connection:
            self.cursor.close()
            self.connection.close()
            "Disconnected from the database."
        else:
            return "No active connection to disconnect."

    def execute_query(self, query, params=None):
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
            print("Query executed successfully.")
        except Exception as e:
            return f"Error: Unable to execute the query - {e}"

    def fetch_data(self, query, params=None):
        try:
            self.cursor.execute(query, params)
            column_names = [desc[0] for desc in self.cursor.description]
            rows = self.cursor.fetchall()

            result = []
            for row in rows:
                cleaned_row = {}
                for i, column_name in enumerate(column_names):
      
                    if i < len(row):
                        value = row[i]
                        if isinstance(value, bytes):
 
                            cleaned_row[column_name] = base64.b64encode(value).decode('utf-8')
                        else:
                            cleaned_row[column_name] = value
                    else:
                        cleaned_row[column_name] = None  

                result.append(cleaned_row)

            return result
        except Exception as e:
            return f"Error: Unable to fetch data - {e}"
        
    def fetch(self, query, params=None):
        try:
            self.cursor.execute(query, params)
            column_names = [desc[0] for desc in self.cursor.description]
            row = self.cursor.fetchone()
            if row is not None:
                result = (dict(zip(column_names, row)))
                row = self.cursor.fetchone()
                return result
        except Exception as e:
            return f"Error: Unable to fetch data - {e}"


