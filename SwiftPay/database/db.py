import mysql.connector
from mysql.connector import Error
from contextlib import contextmanager

class Database:
    _instance = None
    _connection = None
    
    DB_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'swiftpay',
        'autocommit': False,
        'charset': 'utf8mb4',
        'collation': 'utf8mb4_unicode_ci'
    }
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if Database._connection is None:
            self.connect()
    
    def connect(self):
        try:
            config_no_db = {k: v for k, v in self.DB_CONFIG.items() if k != 'database'}
            temp_conn = mysql.connector.connect(**config_no_db)
            cursor = temp_conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.DB_CONFIG['database']}")
            cursor.close()
            temp_conn.close()
            
            Database._connection = mysql.connector.connect(**self.DB_CONFIG)
            print("Database connection established successfully")
            return True
            
        except Error as e:
            print(f"Error connecting to database: {e}")
            return False
    
    @property
    def connection(self):
        if Database._connection is None or not Database._connection.is_connected():
            self.connect()
        return Database._connection
    
    @contextmanager
    def get_cursor(self, dictionary=True):
        cursor = None
        try:
            cursor = self.connection.cursor(dictionary=dictionary)
            yield cursor
            self.connection.commit()
        except Error as e:
            self.connection.rollback()
            raise e
        finally:
            if cursor:
                cursor.close()
    
    def execute_query(self, query, params=None, fetch_one=False, fetch_all=True):
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, params or ())
                if fetch_one:
                    return cursor.fetchone()
                elif fetch_all:
                    return cursor.fetchall()
                return None
        except Error as e:
            print(f"Query error: {e}")
            return None
    
    def execute_insert(self, query, params=None):
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, params or ())
                return cursor.lastrowid
        except Error as e:
            print(f"Insert error: {e}")
            return None
    
    def execute_update(self, query, params=None):
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, params or ())
                return cursor.rowcount
        except Error as e:
            print(f"Update error: {e}")
            return -1
    
    def execute_many(self, query, data_list):
        try:
            with self.get_cursor() as cursor:
                cursor.executemany(query, data_list)
                return cursor.rowcount
        except Error as e:
            print(f"Batch execution error: {e}")
            return -1
    
    def call_procedure(self, proc_name, params=None):
        try:
            with self.get_cursor() as cursor:
                cursor.callproc(proc_name, params or ())
                results = []
                for result in cursor.stored_results():
                    results.extend(result.fetchall())
                return results
        except Error as e:
            print(f"Procedure error: {e}")
            return None
    
    def table_exists(self, table_name):
        query = """
            SELECT COUNT(*) as count 
            FROM information_schema.tables 
            WHERE table_schema = %s AND table_name = %s
        """
        result = self.execute_query(query, (self.DB_CONFIG['database'], table_name), fetch_one=True)
        return result and result.get('count', 0) > 0
    
    def initialize_schema(self, schema_file='database/schema.sql'):
        try:
            with open(schema_file, 'r', encoding='utf-8') as f:
                schema = f.read()
            
            statements = [s.strip() for s in schema.split(';') if s.strip()]
            
            with self.get_cursor() as cursor:
                for statement in statements:
                    if statement and not statement.startswith('--'):
                        try:
                            cursor.execute(statement)
                        except Error as e:
                            if e.errno != 1062:
                                print(f"Schema statement error: {e}")
            
            print("Database schema initialized successfully")
            return True
            
        except FileNotFoundError:
            print(f"Schema file not found: {schema_file}")
            return False
        except Error as e:
            print(f"Schema initialization error: {e}")
            return False
    
    def close(self):
        if Database._connection and Database._connection.is_connected():
            Database._connection.close()
            Database._connection = None
    
    def __del__(self):
        try:
            self.close()
        except:
            pass

db = Database()
