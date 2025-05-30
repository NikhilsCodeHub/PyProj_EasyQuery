from langchain_community.utilities import SQLDatabase

db = SQLDatabase.from_uri("sqlite:///Chinoook.db")
print(db.dialect)
print(db.get_usable_table_names())
# db.run("SELECT name FROM sqlite_master LIMIT 10;")
db.run("SELECT * FROM Artist LIMIT 10;")