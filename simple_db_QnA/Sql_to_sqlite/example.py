"""
Example script demonstrating how to use the SQL Server to SQLite data transfer tool.
"""

from sql_to_sqlite import SQLServerToSQLite

def example_with_direct_api():
    """
    Example of using the SQLServerToSQLite class directly in your code.
    """
    # SQL Server connection string
    # Replace these values with your actual SQL Server details
    server = "OnPrem-SBX-DB01"
    database = "Sample_DB"
    #username = "your_username"
    #password = "your_password"
    
    # Option 1: SQL Server Authentication
    #conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}"
    
    # Option 2: Windows Authentication
    conn_str = f"DRIVER={{SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;"
    
    # List of tables to transfer
    '''
    Example tables to transfer: 
    [SAMPLE_DB].[dbo].[RX_CLAIM]
    [SAMPLE_DB].[dbo].[CLIENT] 
    [SAMPLE_DB].[AO].[drug]
    [AO].[providers]

    
    '''
    
    tables_to_transfer = ["[AO].[Providers]","[AO].[drug_category]","[AO].[drug_name]"]
    
    # Initialize the transfer object
    transfer = SQLServerToSQLite(
        sql_server_conn_str=conn_str,
        sqlite_db_path="example_output.db",  # Custom SQLite database name
        max_rows=100000  # Custom row limit
    )
    
    # Execute the transfer
    transfer.transfer_data(tables_to_transfer)

def example_command_line_usage():
    """
    Example of command line usage (for documentation purposes only).
    This function doesn't actually run anything, it just shows example commands.
    """
    print("Example command line usage:")
    print("\n1. Using SQL Server Authentication:")
    print("python sql_to_sqlite.py --server your_server --database your_database --username your_username --password your_password --tables \"Customers,Orders,Products\"")
    
    print("\n2. Using Windows Authentication:")
    print("python sql_to_sqlite.py --server your_server --database your_database --tables \"Customers,Orders,Products\" --trusted-connection")
    
    print("\n3. Specifying custom SQLite database and row limit:")
    print("python sql_to_sqlite.py --server your_server --database your_database --username your_username --password your_password --tables \"Customers,Orders\" --sqlite-db \"custom_output.db\" --max-rows 50000")

if __name__ == "__main__":
    # Uncomment the line below to run the direct API example
    example_with_direct_api()
    
    # Show command line examples
    # example_command_line_usage()
