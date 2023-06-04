from dotenv import load_dotenv
import psycopg2
import os
import json
from pprint import pprint

load_dotenv()

hostname = os.environ.get("DB_HOST_NAME")
port = os.environ.get("DB_PORT")
dbName = os.environ.get("DB_NAME")
user = os.environ.get("DB_USER_NAME")
password = os.environ.get("DB_PASSWORD")

print(hostname, port, dbName, user)


def addJsonToTable(cursor, conn, courseCode, columnName, data):

    # Convert the Python dictionary to a JSON string
    json_data = json.dumps(data)

    update_query = f"UPDATE \"Course\" SET {columnName} = %s WHERE course_code = %s;"
    cursor.execute(update_query, (json_data, courseCode))
    conn.commit()


"""
ADD A NEW COLUMN

table_name = "Course"  # Replace with the name of your table
column_name = "precorequisites_text"  # Replace with the name of the new column

alter_query = f'ALTER TABLE "Course" ADD COLUMN {column_name} JSON;'

cursor.execute(alter_query)

conn.commit()
"""
