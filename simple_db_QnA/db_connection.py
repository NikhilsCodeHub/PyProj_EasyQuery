from langchain_community.utilities import SQLDatabase
import os
from dotenv import load_dotenv

load_dotenv()


# This is for Test DB.
# db = SQLDatabase.from_uri("sqlite:///Chinoook.db")
# print(db.dialect)
# print(db.get_usable_table_names())
# db.run("SELECT name FROM sqlite_master LIMIT 10;")
# db.run("SELECT * FROM Artist LIMIT 10;")


# This is for Sample DB.
db = SQLDatabase.from_uri(os.getenv("DB_URI"))
db._sample_rows_in_table_info = False
#print(db.dialect)
#print(db.get_usable_table_names())
#db.run("SELECT name FROM sqlite_master LIMIT 10;")
#db.run("SELECT * FROM Drugs LIMIT 10;")