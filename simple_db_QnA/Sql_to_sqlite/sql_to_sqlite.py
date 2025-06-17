import argparse
import pyodbc
import sqlite3
import sys
import logging
from typing import List, Dict, Any

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class SQLServerToSQLite:
    def __init__(self, sql_server_conn_str: str, sqlite_db_path: str = "TempData.db", max_rows: int = 100000):
        """
        Initialize the data transfer class.
        
        Args:
            sql_server_conn_str: Connection string for SQL Server
            sqlite_db_path: Path to SQLite database file
            max_rows: Maximum number of rows to retrieve per table
        """
        self.sql_server_conn_str = sql_server_conn_str
        self.sqlite_db_path = sqlite_db_path
        self.max_rows = max_rows
        
    def _extract_table_name(self, full_table_name: str) -> str:
        """
        Extract the table name without the schema prefix.
        
        Args:
            full_table_name: Full table name with schema (e.g., 'schema.table_name')
            
        Returns:
            Table name without schema
        """
        # Split by dot and take the last part as the table name
        if '.' in full_table_name:
            return full_table_name.split('.')[-1]
        return full_table_name
        
    def connect_to_sql_server(self):
        """Connect to SQL Server database."""
        try:
            return pyodbc.connect(self.sql_server_conn_str)
        except pyodbc.Error as e:
            logger.error(f"Failed to connect to SQL Server: {e}")
            raise
            
    def connect_to_sqlite(self):
        """Connect to SQLite database."""
        try:
            return sqlite3.connect(self.sqlite_db_path)
        except sqlite3.Error as e:
            logger.error(f"Failed to connect to SQLite database: {e}")
            raise
            
    def get_table_schema(self, sql_conn, table_name: str) -> List[Dict[str, Any]]:
        """
        Get the schema of a SQL Server table.
        
        Args:
            sql_conn: SQL Server connection
            table_name: Name of the table
            
        Returns:
            List of column information dictionaries
        """
        try:
            cursor = sql_conn.cursor()
            
            # First get column information from INFORMATION_SCHEMA for more detailed type info
            schema_name = 'dbo'  # Default schema
            table_only = table_name
            
            # Extract schema if provided in table_name
            if '.' in table_name and '[' in table_name:
                # Format like [schema].[table]
                parts = table_name.split('.')
                schema_name = parts[0].strip('[]')
                table_only = parts[1].strip('[]')
            elif '.' in table_name:
                # Format like schema.table
                parts = table_name.split('.')
                schema_name = parts[0]
                table_only = parts[1]
                
            try:
                # Get detailed column information from SQL Server
                info_schema_query = f"""
                SELECT 
                    COLUMN_NAME, 
                    DATA_TYPE,
                    CHARACTER_MAXIMUM_LENGTH,
                    NUMERIC_PRECISION,
                    NUMERIC_SCALE,
                    IS_NULLABLE
                FROM 
                    INFORMATION_SCHEMA.COLUMNS 
                WHERE 
                    TABLE_SCHEMA = '{schema_name}' AND 
                    TABLE_NAME = '{table_only}'
                ORDER BY 
                    ORDINAL_POSITION
                """
                
                cursor.execute(info_schema_query)
                column_info = {}
                
                for row in cursor.fetchall():
                    col_name = row[0]
                    data_type = row[1]
                    max_length = row[2]
                    precision = row[3]
                    scale = row[4]
                    is_nullable = row[5]
                    
                    column_info[col_name] = {
                        "sql_type": data_type,
                        "max_length": max_length,
                        "precision": precision,
                        "scale": scale,
                        "is_nullable": is_nullable == 'YES'
                    }
                    
                logger.info(f"Retrieved detailed schema information for {table_name}")
            except Exception as schema_error:
                logger.warning(f"Could not get detailed schema info: {schema_error}. Using basic schema detection.")
                column_info = {}
            
            # Now get basic column info and map to SQLite types
            cursor.execute(f"SELECT * FROM {table_name} WHERE 1=0")
            columns = []
            
            for i, column in enumerate(cursor.description):
                col_name = column[0]
                col_type_name = column[1].__name__
                sqlite_type = self._map_sql_type_to_sqlite(col_type_name)
                
                col_info = {
                    "name": col_name,
                    "type": sqlite_type,
                    "sql_server_type": col_type_name,
                    "column_id": i
                }
                
                # Add detailed info if available
                if col_name in column_info:
                    col_info.update(column_info[col_name])
                    
                columns.append(col_info)
                
            cursor.close()
            
            # Log column information for debugging
            # logger.info(f"Table {table_name} schema:")
            #for col in columns:
            #    logger.info(f"Column: {col['name']}, SQL Type: {col.get('sql_server_type', 'unknown')}, SQLite Type: {col['type']}")
                
            return columns
        except pyodbc.Error as e:
            logger.error(f"Failed to get schema for table {table_name}: {e}")
            raise
            
    def _map_sql_type_to_sqlite(self, sql_type: str) -> str:
        """
        Map SQL Server data types to SQLite data types.
        
        Args:
            sql_type: SQL Server data type
            
        Returns:
            Corresponding SQLite data type
        """
        # Python type names (from pyodbc)
        python_type_mapping = {
            "str": "TEXT",
            "int": "INTEGER",
            "bool": "INTEGER",
            "datetime": "TEXT",
            "date": "TEXT",
            "time": "TEXT",
            "bytes": "BLOB",
            "Decimal": "REAL",
            "float": "REAL",
            "money": "REAL",
            "numeric": "REAL",
            "NoneType": "NULL",
        }
        
        # SQL Server native type names (from INFORMATION_SCHEMA)
        sql_server_type_mapping = {
            # Character types
            "char": "TEXT",
            "varchar": "TEXT",
            "text": "TEXT",
            "nchar": "TEXT",
            "nvarchar": "TEXT",
            "ntext": "TEXT",
            
            # Numeric types
            "bit": "INTEGER",
            "tinyint": "INTEGER",
            "smallint": "INTEGER",
            "int": "INTEGER",
            "bigint": "INTEGER",
            "decimal": "TEXT",  # Use TEXT to preserve precision
            "numeric": "TEXT",  # Use TEXT to preserve precision
            "smallmoney": "TEXT",
            "money": "TEXT",
            "float": "REAL",
            "real": "REAL",
            
            # Date and time types
            "datetime": "TEXT",
            "smalldatetime": "TEXT",
            "date": "TEXT",
            "time": "TEXT",
            "datetimeoffset": "TEXT",
            "datetime2": "TEXT",
            
            # Binary types
            "binary": "BLOB",
            "varbinary": "BLOB",
            "image": "BLOB",
            
            # Other types
            "uniqueidentifier": "TEXT",
            "xml": "TEXT",
            "sql_variant": "TEXT",
            "timestamp": "BLOB",
            "rowversion": "BLOB",
            "hierarchyid": "TEXT",
            "geography": "BLOB",
            "geometry": "BLOB"
        }
        
        # First check if it's a Python type name
        if sql_type in python_type_mapping:
            return python_type_mapping[sql_type]
            
        # Then check if it's a SQL Server type name
        if sql_type.lower() in sql_server_type_mapping:
            return sql_server_type_mapping[sql_type.lower()]
            
        # Default to TEXT for unknown types
        logger.warning(f"Unknown SQL type: {sql_type}, mapping to TEXT")
        return "TEXT"
        
    def create_sqlite_table(self, sqlite_conn, table_name: str, columns: List[Dict[str, Any]]):
        """
        Create a table in SQLite database.
        
        Args:
            sqlite_conn: SQLite connection
            table_name: Name of the table (may include schema)
            columns: List of column information dictionaries
        """
        try:
            cursor = sqlite_conn.cursor()
            
            # Extract table name without schema for SQLite
            sqlite_table_name = self._extract_table_name(table_name)
            
            # Drop table if exists
            cursor.execute(f"DROP TABLE IF EXISTS {sqlite_table_name}")
            
            # Create table
            column_defs = [f"{col['name']} {col['type']}" for col in columns]
            create_table_sql = f"CREATE TABLE {sqlite_table_name} ({', '.join(column_defs)})"
            
            cursor.execute(create_table_sql)
            sqlite_conn.commit()
            cursor.close()
            
            logger.info(f"Created table {sqlite_table_name} in SQLite database (from {table_name})")
        except sqlite3.Error as e:
            logger.error(f"Failed to create table {table_name} in SQLite: {e}")
            raise
            
    def transfer_data(self, table_list: List[str]):
        """
        Transfer data from SQL Server to SQLite for the specified tables.
        
        Args:
            table_list: List of table names to transfer
        """
        sql_conn = self.connect_to_sql_server()
        sqlite_conn = self.connect_to_sqlite()
        
        for table_name in table_list:
            try:
                logger.info(f"Processing table: {table_name}")
                
                # Get table schema
                columns = self.get_table_schema(sql_conn, table_name)
                
                # Create table in SQLite
                self.create_sqlite_table(sqlite_conn, table_name, columns)
                
                # Transfer data
                self._copy_data(sql_conn, sqlite_conn, table_name, columns)
                
                logger.info(f"Completed transfer for table: {table_name}")
            except Exception as e:
                logger.error(f"Failed to transfer table {table_name}: {e}")
                continue
                
        sql_conn.close()
        sqlite_conn.close()
        logger.info("Data transfer completed")
        
    def _convert_row_for_sqlite(self, row, columns):
        """
        Convert row data to SQLite compatible types.
        
        Args:
            row: Row data from SQL Server
            columns: Column information
            
        Returns:
            Converted row data
        """
        converted_row = []
        for i, value in enumerate(row):
            # Skip conversion for None values
            if value is None:
                converted_row.append(None)
                continue
                
            # Get column information
            col_info = columns[i] if i < len(columns) else {"type": "TEXT"}
            col_type = col_info["type"]
            sql_type = col_info.get("sql_type", "").lower()
            sql_server_type = col_info.get("sql_server_type", "").lower()
            
            # Special handling for problematic types
            if sql_type == "uniqueidentifier" or "uniqueidentifier" in sql_server_type:
                # Convert GUID/UUID to string
                try:
                    converted_row.append(str(value))
                except Exception:
                    converted_row.append("")
                continue
                
            if sql_type in ["timestamp", "rowversion"] or "timestamp" in sql_server_type or "rowversion" in sql_server_type:
                # Convert timestamp/rowversion to bytes or hex string
                if isinstance(value, bytes):
                    converted_row.append(value)
                else:
                    try:
                        # Try to convert to hex string
                        converted_row.append(str(value))
                    except Exception:
                        converted_row.append("")
                continue
                
            if sql_type in ["varbinary", "binary", "image"] or "binary" in sql_server_type or "image" in sql_server_type:
                # Handle binary data
                if isinstance(value, bytes):
                    converted_row.append(value)
                else:
                    try:
                        # If it's not bytes already, try to encode as bytes
                        if isinstance(value, str):
                            converted_row.append(value.encode('utf-8', errors='replace'))
                        else:
                            converted_row.append(str(value).encode('utf-8', errors='replace'))
                    except Exception as e:
                        logger.error(f"Error converting binary data: {e}")
                        converted_row.append(b'')
                continue
                
            # Standard type conversions
            if col_type == 'TEXT':
                # Convert any non-string types to string
                if not isinstance(value, str):
                    try:
                        converted_row.append(str(value))
                    except Exception:
                        # If conversion fails, use empty string
                        converted_row.append('')
                else:
                    converted_row.append(value)
            elif col_type == 'INTEGER':
                # Convert to integer
                try:
                    converted_row.append(int(value))
                except (ValueError, TypeError):
                    # If conversion fails, use 0
                    converted_row.append(0)
            elif col_type == 'REAL':
                # Convert to float
                try:
                    converted_row.append(float(value))
                except (ValueError, TypeError):
                    # If conversion fails, use 0.0
                    converted_row.append(0.0)
            elif col_type == 'BLOB':
                # Ensure binary data is properly handled
                if isinstance(value, bytes):
                    converted_row.append(value)
                else:
                    try:
                        # Try to convert to bytes if not already
                        if isinstance(value, str):
                            converted_row.append(value.encode('utf-8', errors='replace'))
                        else:
                            converted_row.append(str(value).encode('utf-8', errors='replace'))
                    except Exception:
                        # If conversion fails, use empty bytes
                        converted_row.append(b'')
            else:
                # Default to string conversion for unknown types
                try:
                    converted_row.append(str(value))
                except Exception:
                    converted_row.append('')
                    
        return converted_row
    
    def _copy_data(self, sql_conn, sqlite_conn, table_name: str, columns: List[Dict[str, Any]]):
        """
        Copy data from SQL Server table to SQLite table.
        
        Args:
            sql_conn: SQL Server connection
            sqlite_conn: SQLite connection
            table_name: Name of the table (may include schema)
            columns: List of column information dictionaries
        """
        try:
            # Extract table name without schema for SQLite
            sqlite_table_name = self._extract_table_name(table_name)
            
            # Get data from SQL Server (using original table name with schema)
            sql_cursor = sql_conn.cursor()
            sql_cursor.execute(f"SELECT TOP {self.max_rows} * FROM {table_name}")
            logger.info(f"Got data from SQL Server for table {table_name}") 


            # Prepare SQLite for insertion (using table name without schema)
            column_names = [col['name'] for col in columns]
            placeholders = ', '.join(['?' for _ in columns])
            insert_sql = f"INSERT INTO {sqlite_table_name} ({', '.join(column_names)}) VALUES ({placeholders})"
            

            # Insert data in batches
            sqlite_cursor = sqlite_conn.cursor()
            batch_size = 1000
            batch = []
            row_count = 0
            error_count = 0
            logger.info(f"Starting data transfer for table {table_name} to {sqlite_table_name}")
            
            for row in sql_cursor:
                try:
                    # Convert row data to SQLite compatible types
                    converted_row = self._convert_row_for_sqlite(row, columns)
                    batch.append(converted_row)
                    row_count += 1
                    
                    #--- Commented out as it may produce too much log output
                    #if row_count <= 5:  # Log only first few rows for debugging
                        #logger.info(f"Row {row_count}: Original: {row}")
                        #logger.info(f"Row {row_count}: Converted: {converted_row}")
                        
                    if len(batch) >= batch_size:
                        try:
                            sqlite_cursor.executemany(insert_sql, batch)
                            sqlite_conn.commit()
                            logger.info(f"Inserted {len(batch)} rows into {sqlite_table_name}")
                        except sqlite3.Error as e:
                            logger.error(f"Batch insert error: {e}")
                            # Try inserting rows one by one to identify problematic rows
                            for i, single_row in enumerate(batch):
                                try:
                                    sqlite_cursor.execute(insert_sql, single_row)
                                    sqlite_conn.commit()
                                except sqlite3.Error as row_error:
                                    error_count += 1
                                    logger.error(f"Error inserting row {row_count - len(batch) + i + 1}: {row_error}")
                                    logger.error(f"Problematic row data: {single_row}")
                                    # Log column names and types for debugging
                                    for col_idx, col_val in enumerate(single_row):
                                        col_name = columns[col_idx]['name'] if col_idx < len(columns) else f"Column {col_idx}"
                                        logger.error(f"Column {col_idx} ({col_name}): {col_val} (type: {type(col_val).__name__})")
                        batch = []
                except Exception as row_ex:
                    error_count += 1
                    logger.error(f"Error processing row {row_count}: {row_ex}")
                    logger.error(f"Problematic row data: {row}")
                    
            # Insert remaining rows
            if batch:
                try:
                    sqlite_cursor.executemany(insert_sql, batch)
                    sqlite_conn.commit()
                    logger.info(f"Inserted final {len(batch)} rows into {sqlite_table_name}")
                except sqlite3.Error as e:
                    logger.error(f"Final batch insert error: {e}")
                    # Try inserting rows one by one
                    for i, single_row in enumerate(batch):
                        try:
                            sqlite_cursor.execute(insert_sql, single_row)
                            sqlite_conn.commit()
                        except sqlite3.Error as row_error:
                            error_count += 1
                            logger.error(f"Error inserting row {row_count - len(batch) + i + 1}: {row_error}")
                            logger.error(f"Problematic row data: {single_row}")
                
            sql_cursor.close()
            sqlite_cursor.close()
            
            if error_count > 0:
                logger.warning(f"Completed with {error_count} errors. {row_count - error_count} of {row_count} rows transferred from {table_name} to {sqlite_table_name}")
            else:
                logger.info(f"Total {row_count} rows transferred from {table_name} to {sqlite_table_name}")
        except (pyodbc.Error, sqlite3.Error) as e:
            logger.error(f"Error during data copy for table {table_name}: {e}")
            raise

def main():
    parser = argparse.ArgumentParser(description='Transfer data from SQL Server to SQLite')
    parser.add_argument('--server', required=True, help='SQL Server name')
    parser.add_argument('--database', required=True, help='SQL Server database name')
    parser.add_argument('--username', help='SQL Server username')
    parser.add_argument('--password', help='SQL Server password')
    parser.add_argument('--tables', required=True, help='Comma-separated list of tables to transfer')
    parser.add_argument('--sqlite-db', default='TempData.db', help='SQLite database file path')
    parser.add_argument('--max-rows', type=int, default=100000, help='Maximum rows to retrieve per table')
    parser.add_argument('--trusted-connection', action='store_true', help='Use Windows authentication')
    
    args = parser.parse_args()
    
    # Build connection string
    if args.trusted_connection:
        conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={args.server};DATABASE={args.database};Trusted_Connection=yes;"
    else:
        if not args.username or not args.password:
            logger.error("Username and password are required when not using Windows authentication")
            sys.exit(1)
        conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={args.server};DATABASE={args.database};UID={args.username};PWD={args.password}"
    
    # Parse table list
    table_list = [table.strip() for table in args.tables.split(',')]
    
    # Initialize and run transfer
    transfer = SQLServerToSQLite(conn_str, args.sqlite_db, args.max_rows)
    transfer.transfer_data(table_list)

if __name__ == "__main__":
    main()
