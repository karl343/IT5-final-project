"""
SwiftPay Database Connection Module
Handles all database connections and operations
"""

import mysql.connector
from mysql.connector import Error
from contextlib import contextmanager


class Database:
    """
    Database connection class for SwiftPay Payroll System.
    Implements singleton pattern to ensure single database connection.
    """
    
    _instance = None
    _connection = None
    
    # Database configuration - Update these values for your environment
    DB_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'password': '',  # Update with your MySQL password
        'database': 'swiftpay',
        'autocommit': False,
        'charset': 'utf8mb4',
        'collation': 'utf8mb4_unicode_ci'
    }
    
    def __new__(cls):
        """Singleton pattern implementation"""
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize database connection"""
        if Database._connection is None:
            self.connect()
    
    def connect(self):
        """
        Establish connection to MySQL database.
        Creates database if it doesn't exist.
        """
        try:
            # First connect without database to create it if needed
            config_no_db = {k: v for k, v in self.DB_CONFIG.items() if k != 'database'}
            temp_conn = mysql.connector.connect(**config_no_db)
            cursor = temp_conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.DB_CONFIG['database']}")
            cursor.close()
            temp_conn.close()
            
            # Now connect with database
            Database._connection = mysql.connector.connect(**self.DB_CONFIG)
            print("Database connection established successfully")
            return True
            
        except Error as e:
            print(f"Error connecting to database: {e}")
            return False
    
    @property
    def connection(self):
        """Get the database connection, reconnect if necessary"""
        if Database._connection is None or not Database._connection.is_connected():
            self.connect()
        return Database._connection
    
    @contextmanager
    def get_cursor(self, dictionary=True):
        """
        Context manager for database cursor.
        Automatically handles commit/rollback and cursor cleanup.
        
        Args:
            dictionary: If True, return results as dictionaries
            
        Yields:
            MySQL cursor object
        """
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
        """
        Execute a SELECT query and return results.
        
        Args:
            query: SQL query string
            params: Query parameters (tuple or dict)
            fetch_one: If True, fetch single result
            fetch_all: If True, fetch all results
            
        Returns:
            Query results or None
        """
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
        """
        Execute an INSERT query and return the last inserted ID.
        
        Args:
            query: SQL INSERT query
            params: Query parameters
            
        Returns:
            Last inserted ID or None on error
        """
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, params or ())
                return cursor.lastrowid
        except Error as e:
            print(f"Insert error: {e}")
            return None
    
    def execute_update(self, query, params=None):
        """
        Execute an UPDATE or DELETE query.
        
        Args:
            query: SQL UPDATE/DELETE query
            params: Query parameters
            
        Returns:
            Number of affected rows or -1 on error
        """
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, params or ())
                return cursor.rowcount
        except Error as e:
            print(f"Update error: {e}")
            return -1
    
    def execute_many(self, query, data_list):
        """
        Execute a query with multiple data sets (batch insert/update).
        
        Args:
            query: SQL query string
            data_list: List of parameter tuples
            
        Returns:
            Number of affected rows or -1 on error
        """
        try:
            with self.get_cursor() as cursor:
                cursor.executemany(query, data_list)
                return cursor.rowcount
        except Error as e:
            print(f"Batch execution error: {e}")
            return -1
    
    def call_procedure(self, proc_name, params=None):
        """
        Call a stored procedure.
        
        Args:
            proc_name: Name of the stored procedure
            params: Procedure parameters
            
        Returns:
            Procedure results or None
        """
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
        """
        Check if a table exists in the database.
        
        Args:
            table_name: Name of the table to check
            
        Returns:
            Boolean indicating if table exists
        """
        query = """
            SELECT COUNT(*) as count 
            FROM information_schema.tables 
            WHERE table_schema = %s AND table_name = %s
        """
        result = self.execute_query(query, (self.DB_CONFIG['database'], table_name), fetch_one=True)
        return result and result.get('count', 0) > 0
    
    def initialize_schema(self, schema_file='database/schema.sql'):
        """
        Initialize database schema from SQL file.
        
        Args:
            schema_file: Path to schema SQL file
        """
        try:
            with open(schema_file, 'r', encoding='utf-8') as f:
                schema = f.read()
            
            # Split by semicolon and execute each statement
            statements = [s.strip() for s in schema.split(';') if s.strip()]
            
            with self.get_cursor() as cursor:
                for statement in statements:
                    if statement and not statement.startswith('--'):
                        try:
                            cursor.execute(statement)
                        except Error as e:
                            # Skip duplicate key errors for sample data
                            if e.errno != 1062:  # Duplicate entry
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
        """Close the database connection"""
        if Database._connection and Database._connection.is_connected():
            Database._connection.close()
            Database._connection = None
            # Connection closed message removed - normal cleanup behavior
    
    def __del__(self):
        """Destructor to close connection"""
        try:
            self.close()
        except:
            pass  # Ignore errors during cleanup


# Create a global database instance
db = Database()

