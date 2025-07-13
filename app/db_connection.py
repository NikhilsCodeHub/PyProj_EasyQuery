from langchain_community.utilities import SQLDatabase
import os
#from dotenv import load_dotenv

#load_dotenv()


# This is for Sample DB.
db = SQLDatabase.from_uri(os.getenv("DB_URI"), view_support=True, max_string_length=8000)
db._sample_rows_in_table_info = 0
#print(db.dialect)
#print(db.get_usable_table_names())
