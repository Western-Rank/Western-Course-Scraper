from dotenv import load_dotenv
import psycopg2
import os
from pprint import pprint

load_dotenv()

hostname = os.environ.get("DB_HOST_NAME")
port = os.environ.get("DB_PORT")
dbName = os.environ.get("DB_NAME")
user = os.environ.get("DB_USER_NAME")
password = os.environ.get("DB_PASSWORD")

print(hostname, port, dbName, user)


conn = psycopg2.connect(
    host=hostname,
    port=port,
    database=dbName,
    user=user,
    password=password
)

# Query to retrieve table names from the database catalog
cursor = conn.cursor()

# Execute a query to fetch the column names of a table
table_name = "Course"
query = f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}'"
cursor.execute(query)

# Fetch all the column names from the result set
column_names = [row[0] for row in cursor.fetchall()]
print("??")
# Print the column names
for column_name in column_names:
    print(column_name)

# Close the cursor and connection
cursor.close()
conn.close()


""" 
cursor.execute('SELECT * FROM "Course" WHERE course_code = "EPID 2200A/B"')

row = cursor.fetchone()
print(row)

cursor.close()
conn.close()
 """
