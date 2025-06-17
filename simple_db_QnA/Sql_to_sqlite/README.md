# SQL Server to SQLite Data Transfer Tool

This Python script transfers data from SQL Server tables to a SQLite database.

## Features

- Transfers data from SQL Server to SQLite
- Automatically creates tables in SQLite with appropriate data types
- Handles large datasets with batch processing
- Limits the number of rows transferred (default: 100,000 rows per table)
- Supports Windows authentication and SQL Server authentication

## Requirements

- Python 3.6+
- Required Python packages:
  - pyodbc
  - sqlite3 (included in Python standard library)

## Installation

1. Install the required Python packages:

```bash
pip install pyodbc
```

2. Make sure you have the appropriate ODBC driver for SQL Server installed on your system.

## Usage

```bash
python sql_to_sqlite.py --server SERVER_NAME --database DB_NAME --tables "Table1,Table2,Table3" [OPTIONS]
```

### Required Arguments

- `--server`: SQL Server name
- `--database`: SQL Server database name
- `--tables`: Comma-separated list of tables to transfer

### Optional Arguments

- `--username`: SQL Server username (required if not using Windows authentication)
- `--password`: SQL Server password (required if not using Windows authentication)
- `--sqlite-db`: SQLite database file path (default: TempData.db)
- `--max-rows`: Maximum number of rows to retrieve per table (default: 100000)
- `--trusted-connection`: Use Windows authentication instead of SQL Server authentication

## Examples

### Using SQL Server Authentication

```bash
python sql_to_sqlite.py --server myserver --database mydatabase --username myuser --password mypassword --tables "Customers,Orders,Products"
```

### Using Windows Authentication

```bash
python sql_to_sqlite.py --server myserver --database mydatabase --tables "Customers,Orders,Products" --trusted-connection
```

### Specifying SQLite Database Path and Row Limit

```bash
python sql_to_sqlite.py --server myserver --database mydatabase --username myuser --password mypassword --tables "Customers,Orders" --sqlite-db "C:/Data/my_database.db" --max-rows 50000
```

## How It Works

1. The script connects to the specified SQL Server database
2. For each table in the provided list:
   - Retrieves the table schema from SQL Server
   - Creates a corresponding table in SQLite with appropriate data types
   - Transfers data in batches (1000 rows at a time) to optimize performance
   - Logs progress and any errors encountered
3. The SQLite database is created in the specified location (default: TempData.db in the current directory)

## Error Handling

- The script includes comprehensive error handling and logging
- If an error occurs while processing a specific table, the script will log the error and continue with the next table
- Connection errors, schema retrieval errors, and data transfer errors are all handled appropriately
