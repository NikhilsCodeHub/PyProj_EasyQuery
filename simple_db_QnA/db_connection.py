from langchain_community.utilities import SQLDatabase


# This is for Test DB.
# db = SQLDatabase.from_uri("sqlite:///Chinoook.db")
# print(db.dialect)
# print(db.get_usable_table_names())
# db.run("SELECT name FROM sqlite_master LIMIT 10;")
# db.run("SELECT * FROM Artist LIMIT 10;")


# This is for Sample DB.
db = SQLDatabase.from_uri("sqlite:///Sample_DB.db")
print(db.dialect)
print(db.get_usable_table_names())
db.run("SELECT name FROM sqlite_master LIMIT 10;")
db.run("SELECT * FROM Drugs LIMIT 10;")