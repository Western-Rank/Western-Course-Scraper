from dotenv import load_dotenv
import psycopg2
import os
from pprint import pprint
import json

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

emptyJson = json.dumps({})

# Execute a query to fetch the column names of a table
table_name = "Course"
updateCourseInfo_query = f'UPDATE "Course" SET course_name = %s, prerequisites_text = %s, antirequisites_text = %s, corequisites_text = %s, precorequisites_text = %s, description = %s, location = %s, extra_info = %s WHERE course_code = %s;'
cursor.execute(updateCourseInfo_query, (
    "INDIGENOUS WOMEN IN THE ARTS IN CANADA: CULTURAL TRADITIONS, SURVIVAL, AND COLONIAL RESISTANCE", emptyJson, emptyJson, emptyJson, emptyJson, "", "", "", "AH 2634F/G"
))

conn.commit()

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
